# import asyncio
# from mcp import ClientSession
# from mcp.client.sse import sse_client

# async def scrape_linkedin():
#     # The MCP URL provided by Bright Data
#     mcp_url = "https://mcp.brightdata.com/sse?token=e47c0c51-175e-4f9a-90ca-974cc3a60f21&groups=advanced_scraping,social"
    
#     # The LinkedIn profile you want to scrape
#     target_profile_url = "https://sg.linkedin.com/in/shuenn-yuen-han-60a467261"
#     # async with sse_client(mcp_url) as (read_stream, write_stream):
#     #     async with ClientSession(read_stream, write_stream) as session:
#     #         # Step 1: Initialize the connection
#     #         await session.initialize()

#     #         # Step 2: Fetch the tools
#     #         # Note: Depending on the SDK version, this returns a ListToolsResult object 
#     #         # with a .tools attribute containing the list of Tool objects.
#     #         tools_result = await session.list_tools()
            
#     #         print(f"--- Found {len(tools_result.tools)} available tools ---")
            
#     #         for tool in tools_result.tools:
#     #             print(f"\nTool Name: {tool.name}")
#     #             print(f"Description: {tool.description}")
#     #             print(f"Arguments Schema: {tool.inputSchema}")

#     async with sse_client(mcp_url) as (read_stream, write_stream):
#         async with ClientSession(read_stream, write_stream) as session:
#             # Initialize the connection with the MCP server
#             await session.initialize()

#             # Call the specific tool for LinkedIn profiles
#             # Bright Data's tool names usually follow the pattern 'linkedin_profile'
#             # We pass the target URL as an argument
#             response = await session.call_tool(
#                 "web_data_linkedin_person_profile", 
#                 arguments={"url": target_profile_url}
#             )

#             # Print the scraped data
#             print("Scraped Data:")
#             print(response.content)

# if __name__ == "__main__":
#     asyncio.run(scrape_linkedin())


import requests
import json

headers = {
    "Authorization": "Bearer e47c0c51-175e-4f9a-90ca-974cc3a60f21",
    "Content-Type": "application/json",
}

data = json.dumps({
    "input": [{"url":"https://www.linkedin.com/in/elad-moshe-05a90413/"},{"url":"https://www.linkedin.com/in/jonathan-myrvik-3baa01109"},{"url":"https://www.linkedin.com/in/aviv-tal-75b81/"},{"url":"https://www.linkedin.com/in/bulentakar/"}],
})

response = requests.post(
    "https://api.brightdata.com/datasets/v3/scrape?dataset_id=gd_l1viktl72bvl7bjuj0&notify=false&include_errors=true",
    headers=headers,
    data=data
)

print(response.json())