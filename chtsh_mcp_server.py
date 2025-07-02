#!/usr/bin/env python3
"""MCP Server for cht.sh"""

import asyncio
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("chtsh-server")


class ChtshClient:
    def __init__(self):
        # aiohttp is in PLAIN_TEXT_AGENTS, so we get clean text output
        self.session = None

    async def query(self, query: str) -> str:
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )

        try:
            url = f"https://cht.sh/{query.strip('/')}"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.text()
        except Exception as e:
            return f"Error: {str(e)}"

    async def close(self):
        if self.session:
            await self.session.close()


chtsh = ChtshClient()


@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="chtsh",
            description="Query cht.sh for cheat sheets and documentation",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Query (e.g., 'git', 'python/list', 'docker')",
                    }
                },
                "required": ["query"],
            },
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "chtsh":
        result = await chtsh.query(arguments["query"])
        return [TextContent(type="text", text=result)]

    raise ValueError(f"Unknown tool: {name}")


async def main():
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream, write_stream, server.create_initialization_options()
            )
    finally:
        await chtsh.close()


if __name__ == "__main__":
    asyncio.run(main())
