import asyncio, base64, json, os, sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
# Smoke test for struktured-labs/mgba-mcp over real MCP stdio.
# Usage (from tools/play-tester): uv run --directory .deps/mgba-mcp python ../../mcp/test_mgba_mcp_client.py
HERE = os.path.dirname(os.path.abspath(__file__))
ROM = os.path.abspath(os.path.join(HERE, "../../../game/pokeemerald.gba"))
OUT = os.path.join(HERE, "../out/") ; os.makedirs(OUT, exist_ok=True)
MGBA_MCP_DIR = os.path.abspath(os.path.join(HERE, "../.deps/mgba-mcp"))
async def main():
    env = dict(os.environ, PATH="/opt/mgba-0.11/bin:" + os.environ["PATH"], LD_LIBRARY_PATH="/opt/mgba-0.11/lib")
    params = StdioServerParameters(command="uv", args=["run", "--directory", MGBA_MCP_DIR, "mgba-mcp"], env=env)
    async with stdio_client(params) as (r, w):
        async with ClientSession(r, w) as s:
            await s.initialize()
            tools = await s.list_tools()
            print("tools:", [t.name for t in tools.tools])
            async def call(name, args, tag):
                res = await s.call_tool(name, args)
                n = 0
                for c in res.content:
                    if c.type == "image":
                        n += 1
                        open(f"{OUT}{tag}_{n}.png", "wb").write(base64.b64decode(c.data))
                    else:
                        print(f"[{tag}] {c.text[:600]}")
                print(f"[{tag}] images: {n}, isError={res.isError}")
            await call("mgba_run", {"rom_path": ROM, "frames": 1800}, "run")
            # ROM header title at 0x080000A0, 12 bytes
            await call("mgba_read_range", {"rom_path": ROM, "start_address": 0x080000A0, "length": 12, "frames": 10}, "header")
            await call("mgba_run_sequence", {"rom_path": ROM, "frames": 2400, "capture_every": 600,
                 "inputs": [{"frame": 1900, "keys": ["START"]}], "timeout": 90}, "seq")
asyncio.run(main())
