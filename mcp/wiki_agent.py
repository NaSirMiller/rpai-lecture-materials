from client import MCPClient
import json
import logging
import ollama
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, Optional, Literal


class Step(BaseModel):
    intent: str
    status: Literal[
        "in_progress",
        "done",
    ]
    function: Optional[Dict[str, Any]] = None
    tool_result: Optional[Dict[str, Any]] = None


class ToolCall(BaseModel):
    name: str
    parameters: Dict[str, Any]


class WikipediaAgent:
    def __init__(
        self,
        client: MCPClient,
        model_name: str,
        max_iterations=10,
    ) -> None:
        self.mcp_client = client
        self.model_name = model_name
        self.most_recent_trace: list[Step] = None
        self.max_iterations = max_iterations
        self.most_recent_summary: str = None

    async def setup(self, mcp_server_path: str) -> None:
        logging.info(f"Connecting to server located at {mcp_server_path}...")
        await self.mcp_client.connect_to_server(mcp_server_path)
        logging.info("Connection to server complete.")
        self.tools = self.mcp_client.get_tools()
        save_format = await self.mcp_client.read_resource(uri="resource://save_format")
        if save_format is None:
            logging.error("The file save format read from the server is not valid.")
            raise ValueError("The file save format read from the server is not valid.")
        self.system_prompt = await self.mcp_client.get_prompt(
            name="default_system_prompt", arguments={"file_save_format": save_format}
        )

    def parse_agent_response(self, response: str) -> Step:
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
            response = (
                response.replace("“", '"').replace("”", '"').lower()
            )  # handles producing non-standard quotes that are unsupported in JSON parsing
            response_as_dict = json.loads(response)
            return Step.model_validate(response_as_dict)
        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(f"Agent has produced invalid JSON: {e}")

    def execute_tool(self, tool_call: Dict[str, Any]) -> dict:
        """
        Executes a callable function/tool given provided parameters.
        """
        if not tool_call:
            return {}
        name = tool_call.get("name")
        params = tool_call.get("parameters", {})
        if name not in [tool.name for tool in self.tools]:
            return {"success": False, "result": f"Unknown tool: {name}"}
        try:
            result = self.mcp_client.call_tool(name=name, arguments=params)
            return {"success": True, "result": result}
        except Exception as e:
            return {"success": False, "result": str(e)}

    def call_llm(self, messages: list[Dict[str, Any]]) -> str:
        """
        Call the LLM and return content based on the current messages.
        """
        response = ollama.chat(model=self.model_name, messages=messages)
        return response.message.content.strip()

    def summarize(self) -> None:
        """
        Summarize the tool calls for the most recent query.
        """
        summarization_prompt = """
        Answer the user's original question based on the following tool calls and results. Be concise.
        """

        trace_summary = "\n".join(
            f"- Intent: {s.intent}, Tool: {s.function}, Result: {s.tool_result}"
            for s in self.most_recent_trace
        )

        messages = [
            {
                "role": "system",
                "content": "You are an expert research agent.",
            },  # clears previous system message, allowing the agent to deal with summarization rather than tool use
            {"role": "user", "content": summarization_prompt + trace_summary},
        ]

        summary = self.call_llm(messages)
        self.most_recent_summary = summary
        return summary

    def run(self, query: str) -> str:
        """
        Emulates the agentic loop.
        """
        self.most_recent_trace = []
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query},
        ]

        for iteration in range(self.max_iterations):
            response = self.call_llm(messages)
            try:
                step = self.parse_agent_response(response)
                print(f"Step {iteration + 1}: {step}")
            except ValueError as e:
                messages.append(
                    {
                        "role": "user",
                        "content": f"Invalid JSON: {e}. Please respond with valid JSON following the schema.",
                    }
                )
                continue

            if step.function:
                if (
                    step.function["name"] == "save_results_to_path"
                    or step.function["name"] == "get_top_k_keywords"
                ) and not step.function["parameters"].get("content"):
                    step.function["parameters"]["content"] = self.most_recent_summary
                tool_result = self.execute_tool(step.function)
                step.tool_result = tool_result
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "function_called": step.function["name"],
                                "parameters": step.function["parameters"],
                                "tool_result": tool_result,
                            }
                        ),
                    }
                )

            self.most_recent_trace.append(step)

            if step.status == "done":
                break
        return self.summarize()
