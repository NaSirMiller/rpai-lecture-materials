from mcp.server.fastmcp import FastMCP

import wikipedia_tools
import resources
import prompts


server = FastMCP("wikipedia_server")

for tool in (getattr(wikipedia_tools, name) for name in wikipedia_tools.__all__):
    server.tool()(tool)

for name in prompts.__all__:
    prompt_func = getattr(prompts, name)
    server.prompt(name)(prompt_func)

for name in resources.__all__:
    resource_func = getattr(resources, name)
    server.resource(f"resource://{name}")(resource_func)

if __name__ == "__main__":
    server.run(transport="stdio")
