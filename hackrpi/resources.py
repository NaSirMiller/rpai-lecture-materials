from langchain_community.vectorstores import FAISS
import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

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


def summary_format() -> str:
    file_save_format: str = """
    Question: {user_question}
    Topic: {topic}
    Summary: {summary}
    """  # format we expect agent to follow when saving results
    return file_save_format


__all__ = ["summary_format"]
