import asyncio
import os
import json
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# 1. Setup Environment
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
BRIGHTDATA_TOKEN = "54e390ba-5978-427d-b9d3-d9a2c0b8b2f3"
BRIGHTDATA_URL = f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_TOKEN}&groups=advanced_scraping,social"

async def main():
    # 2. Initialize Model & Agent
    # Using LiteLlm as you requested previously
    model = LiteLlm(model="openai/gpt-5.1")
    
    insta_agent = LlmAgent(
        name="JB_Trend_Analyst",
        model=model,
        instruction="""
        You are a social media analyst focusing on Johor Bahru (JB).
        1. Use 'web_data_instagram_posts' to scrape hashtag pages like:
           https://www.instagram.com/explore/tags/johorbahru/
           https://www.instagram.com/explore/tags/jbfood/
        2. Analyze the post captions and engagement to identify 2026 trends 
           (e.g., new cafe openings, shopping spots, or events).
        3. Summarize the findings into a 'Trend Report'.
        """,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(url=BRIGHTDATA_URL)
            )
        ],
    )

    # 3. Setup Runner
    session_service = InMemorySessionService()
    runner = Runner(agent=insta_agent, app_name="jb_trends", session_service=session_service)
    session = await session_service.create_session(app_name="jb_trends", user_id="user_1")

    # 4. Execute the Scrape
    prompt = "Scrape the latest posts from #JohorBahru and #JBFood to find the top 3 trending spots in JB right now (Feb 2026)."
    user_input = types.Content(role="user", parts=[types.Part(text=prompt)])

    print("🚀 Connecting to Bright Data Instagram Engine...")
    
    async for event in runner.run_async(session_id=session.id, user_id="user_1", new_message=user_input):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(f"DEBUG: {part.text[:100]}...")

        if event.is_final_response():
            # Join parts to prevent the 'list' AttributeError
            final_report = "".join([p.text for p in event.content.parts if p.text])
            print("\n--- 🇲🇾 JB 2026 Trend Report ---")
            print(final_report)
            
            # Save to JSON
            with open("jb_trends_2026.json", "w") as f:
                json.dump({"report": final_report, "timestamp": "2026-02-28"}, f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())

    