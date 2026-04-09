def summary_format() -> str:
    file_save_format: str = """
    Question: {user_question}
    Topic: {topic}
    Summary: {summary}
    """  # format we expect agent to follow when saving results
    return file_save_format


__all__ = ["summary_format"]
