# Lists the tools exposed by penandlim/mgba-live-mcp over MCP stdio.
import asyncio, os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
async def main():
    p = StdioServerParameters(command=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.deps/mgba-live-mcp/.venv/bin/mgba-live-mcp"), args=[])
    async with stdio_client(p) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            t = await s.list_tools(); print(len(t.tools), [x.name for x in t.tools])
asyncio.run(main())
