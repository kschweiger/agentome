import asyncio

from fastmcp import Client

client = Client("http://localhost:8009/mcp")


async def call_tool(name: str, args: dict = {}):
    async with client:
        result = await client.call_tool(name, args)
        print(result)


print(50 * "-")
asyncio.run(call_tool("list_packages"))
print(50 * "-")
asyncio.run(call_tool("list_versions", {"package": "geo_track_analyzer"}))
print(50 * "-")
asyncio.run(call_tool("get_api", {"package": "geo_track_analyzer", "version": "2.0.1"}))
print(50 * "-")
asyncio.run(
    call_tool(
        "get_symbol",
        {"package": "geo_track_analyzer", "version": "2.0.1", "symbol": "GPXTrack"},
    )
)
print(50 * "-")
asyncio.run(
    call_tool(
        "get_symbol",
        {
            "package": "geo_track_analyzer",
            "version": "2.0.1",
            "symbol": "get_processed_track_data",
        },
    )
)
