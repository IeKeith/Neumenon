import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def list_tools():
    mcp_url = "https://mcp.brightdata.com/sse?token=e47c0c51-175e-4f9a-90ca-974cc3a60f21&groups=advanced_scraping,social"
    
    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # This is the key to finding the real tool names
            tools_result = await session.list_tools()
            
            print(f"--- Detected {len(tools_result.tools)} Tools ---")
            for tool in tools_result.tools:
                print(f"Name: {tool.name}")
                print(f"Parameters: {tool.inputSchema['properties'].keys()}\n")

if __name__ == "__main__":
    asyncio.run(list_tools())