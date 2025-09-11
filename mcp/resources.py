from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from mcp.server.fastmcp import FastMCP

mcp_server = FastMCP("resources")

EMBEDDING_MODEL = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
VECTOR_STORE = FAISS(
    embedding_function=EMBEDDING_MODEL,
    docstore=InMemoryDocstore({}),
    index=faiss.IndexFlatL2(384),  # provides the vectorstore the correct dimensions
    index_to_docstore_id={},
)
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=250,  # number of tokens per chunk
    chunk_overlap=25,  # overlap between chunks to maintain context
)


@mcp_server.resource(uri="resource://save_format")
def summary_format() -> str:
    file_save_format: str = """
    Question: {user_question}
    Topic: {topic}
    Summary: {summary}
    """  # format we expect agent to follow when saving results
    return file_save_format


@mcp_server.resource(uri="data://add_to_vectorstore")
def add_to_vectorstore(content: str) -> list[Document]:
    chunks = TEXT_SPLITTER.split_text(content)
    docs = [Document(page_content=chunk) for chunk in chunks]
    VECTOR_STORE.add_documents(docs)


@mcp_server.resource("data://retrieve_from_vectorstore")
def retrieve_from_vectorstore(query: str, k=2) -> list[Document]:
    relevant_docs = VECTOR_STORE.similarity_search(query, k=k)
    relevant_docs = [doc.page_content for doc in relevant_docs]
    return relevant_docs


if __name__ == "__main__":
    mcp_server.run(
        transport="stdio",
    )
