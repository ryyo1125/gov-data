import asyncio, json, sys
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:8000/mcp") as c:
        tools = await c.list_tools()
        print("=== tools/list ===")
        for t in tools:
            req = (t.inputSchema or {}).get("required", [])
            props = list((t.inputSchema or {}).get("properties", {}).keys())
            print(f"- {t.name}: params={props} required={req}")
        print("\n=== resources ===")
        try:
            for r in await c.list_resources():
                print("-", r.uri, "|", r.name)
        except Exception as e:
            print("resources err:", e)

        print("\n=== call ping ===")
        r = await c.call_tool("ping", {})
        print(json.dumps(r.data, ensure_ascii=False)[:800])

        print("\n=== call search_subsidies (医療、福祉) ===")
        r = await c.call_tool("search_subsidies", {
            "keyword": "医療",
            "industry": "医療、福祉",
            "sort": "created_date",
            "order": "DESC",
            "acceptance": 1,
        })
        print(json.dumps(r.data, ensure_ascii=False)[:1500])

asyncio.run(main())
