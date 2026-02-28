import os
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from dotenv import load_dotenv

load_dotenv()
# 1. Set your API Keys
# You can also set these in your terminal: export GOOGLE_API_KEY='your_key'

BRIGHTDATA_TOKEN = "e47c0c51-175e-4f9a-90ca-974cc3a60f21"

# 2. Configure the Bright Data MCP URL
# Adding groups ensures you have access to the social/scraping tools
BRIGHTDATA_URL = f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_TOKEN}&groups=advanced_scraping,social"

# 3. Initialize the Agent
# Gemini 3 Flash is recommended for its speed and efficiency with tool-calling
brightdata_agent = Agent(
    model="gemini-3-flash",
    name="BrightData_Scraper_Agent",
    instruction="""
    You are a data extraction specialist. 
    Use the provided Bright Data MCP tools to search for and scrape web data.
    When a user asks for a profile, find the URL first if not provided, then scrape it.
    """,
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPServerParams(
                url=BRIGHTDATA_URL,
            ),
        )
    ],
)

# 4. Run a task
user_prompt = "Find and scrape the LinkedIn profile for William Gates (Bill Gates)."
response = brightdata_agent.run(user_prompt)

print("--- Agent Response ---")
print(response.text)