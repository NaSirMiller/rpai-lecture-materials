import json
import ollama
from pydantic import BaseModel, ValidationError
from typing import Any, Callable, Dict, Optional, Literal


class Step(BaseModel):
    intent: str
    status: Literal["in_progress", "done", "request_human_approval"]
    function: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class WikipediaAgent:
    def __init__(
        self, model_name: str, tools: list[Callable], system_prompt: str
    ) -> None:
        self.model_name = model_name
        self.tools = tools
        self.system_prompt = system_prompt

    def parse_agent_response(self, response: str) -> Dict[str, Any]:
        """
        Parses the agent's response to a specific action.

        Args:
            response (str): The response from the age m nt/model.

        Returns:
            Dict[str, Any]: Parsed response containing intent, status, and function call details.

        Raises:
            ValueError: If the response cannot be parsed as valid JSON or does not conform to the expected schema.
        """
        try:
            response = response.replace("“", '"').replace(
                "”", '"'
            )  # handles producing non-standard quotes that are unsupported in JSON parsing
            response_as_dict = json.loads(response)
            step = Step.model_validate(response_as_dict)
            return step.model_dump()
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Failed to parse response as JSON: {e}")

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
