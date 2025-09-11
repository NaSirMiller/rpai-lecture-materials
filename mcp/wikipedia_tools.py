from mcp.server.fastmcp import FastMCP
from langchain_community.tools import WikipediaQueryRun
from langchain.utilities import WikipediaAPIWrapper
import os
import uuid

mcp_server = FastMCP("tools")


@mcp_server.tool()
def save_results_to_path(
    content: str, file_name: str, file_directory: str = None
) -> str:
    """
    Saves the generated content to a file at {path}.

    Args:
        content (str): Results from wikipedia
        file_name (str): Provided file name from user or agent.
        file_directory (str): Where to save results

    Returns:
        str: Stringified uuid

    Raises:
        RuntimeError: If the file cannot be saved
    """
    if content is None:
        print("Agent did not pass any content.")
        raise ValueError("Agent did not pass any content.")
    if file_name is None:
        print("File name was not provided.")
        raise ValueError("File name was not provided.")
    if file_directory is None:
        print("Agent did not provide a path.")
        raise ValueError("Agent did not provide a path.")
    os.makedirs(file_directory, exist_ok=True)
    file_id = str(uuid.uuid4())
    path = os.path.join(file_directory, file_name)
    try:
        with open(path, "w") as f:
            f.write(content)
        print(f"File saved successfully at {path}.")
        return file_id
    except Exception as e:
        print(f"Error saving file: {e}")
        raise RuntimeError(f"Failed to save file: {e}")


@mcp_server.tool()
def read_results_from_path(path: str = None) -> str:
    """
    Reads the content from the specified path.

    Args:
        path (str): Where to read results

    Returns:
        str | None: Content of the file. None if there is no file at the path.

    Raises:
        RuntimeError: If there is an error while reading the file
    """
    if path is None:
        print("User did not provide a path.")
        raise ValueError("User did not provide a path.")
    content: str | None = None
    try:
        with open(path, "r") as f:
            content = f.read()
        print("File read successfully.")
        return content
    except Exception as e:
        print(f"Error reading file: {e}")
        raise RuntimeError(f"Failed to read file: {e}")


@mcp_server.tool()
def get_top_k_keywords(content: str, k: int) -> list[str]:
    """
    Finds most frequent words in the content.

    Args:
        content (str): The content to analyze.
        k (int): The number of top keywords to return.

    Returns:
        list[str]: The top k frequent keywords.
    """
    k = int(k)  # Deal with string inputs
    words = content.split()
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    top_k = sorted(word_freq, key=word_freq.get, reverse=True)[:k]
    return top_k


@mcp_server.tool()
def search_wikipedia(query: str) -> str:
    """
    Searches wikipedia for specific query.

    Args:
        query (str): Question to search for

    Returns:
        str: Wikipedia's response to the question.
    """
    wiki_api = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wiki_api)
    return wiki_tool.run(query)


tools_available = [
    save_results_to_path,
    read_results_from_path,
    get_top_k_keywords,
    search_wikipedia,
]

tools_mapping = {
    "save_results_to_path": save_results_to_path,
    "read_results_from_path": read_results_from_path,
    "get_top_k_keywords": get_top_k_keywords,
    "search_wikipedia": search_wikipedia,
}

if __name__ == "__main__":
    mcp_server.run(
        transport="stdio",
    )
