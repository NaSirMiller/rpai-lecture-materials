from pydantic import BaseModel
from typing import Any, Callable, Dict, Optional, Literal


"""
    {“intent”:…, “status”: “done”/“request_human_approval”, “function”: { “name”:…, “parameters”:{}}}
"""


class Step(BaseModel):
    intent: str
    status: Literal["in_progress", "done", "request_human_approval"]
    function: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class WikipediaAgent:
    def __init__(self, model: Any, tools: list[Callable], system_prompt: str) -> None:
        self.model = model
        self.tools = tools
        self.system_prompt = system_prompt

    def parse_agent_response(self) -> None:
        """
        Parses the agent's response to a specific action.
        """
        pass

    def execute_tool(self) -> None:
        """
        Executes a callable function/tool given provided parameters.
        """
        pass

    def summarize_to_user(self) -> None:
        """
        Summarize the tool calls for the most recent query.
        """
        pass

    def run(self) -> None:
        """
        Emulates the agentic loop.
        """
        pass
