from contextlib import AsyncExitStack
import json
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import requests
from typing import Any, Dict, Optional, List
from dotenv import load_dotenv
import os
from openai import OpenAI


class MCPClient:
    """
    [How to create MCP Client Docs](https://modelcontextprotocol.io/docs/develop/build-client)
    """

    def __init__(self) -> None:
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.tools = None
        self.resources = None
        self.prompts = None

    async def connect_to_server(self, server_script_path: str) -> None:
        """
        Creates connection between this and specified server.

        Args:
            server_script_path (str): Where to find server to connect to, with respect to current filesystem
            - Supports ".py" server files

        Raises:
            ValueError: Provided server script path is not a python file.
        """
        is_valid_extension = server_script_path.endswith(".py")

        if not is_valid_extension:
            raise ValueError(
                f"Provided script path is not supported: {server_script_path}. Must be a .py file."
            )

        run_command = "python"
        server_params = StdioServerParameters(
            command=run_command,
            args=[server_script_path],
            env=None,
        )

        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = (
            stdio_transport  # allows you to read and write to the server respectively
        )
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        await self.session.initialize()
        server_response = await self.session.list_tools()
        self.tools = server_response.tools
        if self.tools:
            logging.info(f"Server has the following tools: {self.tools}")

        server_response = await self.session.list_prompts()
        self.prompts = server_response.prompts
        if self.prompts:
            logging.info(f"Server has the following prompts: {self.prompts}")

        server_response = await self.session.list_resources()
        self.resources = server_response.resources
        if self.resources:
            logging.info(f"Server has the following resources: {self.resources}")

    def get_session(self):
        if self.session is not None:
            return self.session

    def get_tools(self):
        if self.tools is not None:
            return self.tools

    def get_prompts(self):
        if self.prompts is not None:
            return self.prompts

    def get_resources(self):
        if self.resources is not None:
            return self.resources

    async def get_prompt(self, name: str, arguments: dict[str, str]) -> str:
        return await self.session.get_prompt(name=name, arguments=arguments)

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        return await self.session.call_tool(name=name, arguments=arguments)

    async def read_resource(self, uri: str) -> Any:
        return await self.session.read_resource(uri=uri)

    async def close_connection(self) -> None:
        await self.exit_stack.aclose()


class OpenRouterClient:
    def __init__(
        self,
        api_key: str | None = None,
    ) -> None:
        load_dotenv()
        self.api_key = api_key if api_key else os.getenv("OPENROUTER_KEY")
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )

    def chat(
        self,
        model: str = "deepseek/deepseek-r1-distill-llama-70b:free",
        messages: List = [],
    ) -> Dict:  # TODO: Change return type to response string
        # TODO: Add type hint for response
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
        )
        return response
