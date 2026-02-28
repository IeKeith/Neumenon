import asyncio
from openai import OpenAI
from mcp import ClientSession
from mcp.client.sse import sse_client
from dotenv import load_dotenv

load_dotenv()
async def run_bridge():
    # 1. Setup Bright Data MCP connection
    mcp_url = "https://mcp.brightdata.com/mcp?token=e47c0c51-175e-4f9a-90ca-974cc3a60f21&groups=advanced_scraping,social"
    
    async with sse_client(mcp_url) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            
            # Get the list of tools from Bright Data
            tools_result = await session.list_tools()
            
            # 2. Convert MCP tools to OpenAI function format
            openai_tools = []
            for tool in tools_result.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            # 3. Call OpenAI with these tools
            client = OpenAI() # Ensure OPENAI_API_KEY is in your environment
            messages = [{"role": "user", "content": "Scrape the LinkedIn profile https://www.linkedin.com/in/williamhgates"}]
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=openai_tools
            )

            # 4. Handle the tool call (The Bridge)
            tool_call = response.choices.message.tool_calls
            if tool_call:
                import json
                print(f"AI decided to use: {tool_call.function.name}")
                
                # Execute the tool via Bright Data MCP
                result = await session.call_tool(
                    tool_call.function.name, 
                    arguments=json.loads(tool_call.function.arguments)
                )
                
                print("--- Scraped Results ---")
                print(result.content)

if __name__ == "__main__":
    asyncio.run(run_bridge())