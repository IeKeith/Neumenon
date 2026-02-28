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

# 1. Credentials
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
BRIGHTDATA_TOKEN = os.getenv("BRIGHTDATA_TOKEN")
BRIGHTDATA_URL = f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_TOKEN}&groups=advanced_scraping,social"

# Your provided list
target_urls = [
    "https://sg.linkedin.com/in/ray-lai-627aaa239",
    "https://sg.linkedin.com/in/gabriel-kay-a76039240",
    "https://sg.linkedin.com/in/dhyeya-anand-b839b2266",
    "https://sg.linkedin.com/in/adikum",
    "https://sg.linkedin.com/in/ayra-mohammed-a920742a3",
    "https://sg.linkedin.com/in/kelliesim",
    "https://sg.linkedin.com/in/shuenn-yuen-han-60a467261",
    "https://sg.linkedin.com/in/anna-rica-sawit",
    "https://sg.linkedin.com/in/jatlysonang"


]

async def scrape_profile(runner, session_id, url):
    """Executes a single scrape and prints progress logs."""
    print(f"📡 [Sending URL]: {url}")
    
    # We are being very explicit with the tool name here
    prompt = f"Use 'web_data_linkedin_person_profile' to scrape this profile: {url}. Summarize their SUTD education and role."
    user_input = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    final_text = ""
    async for event in runner.run_async(session_id=session_id, user_id="user", new_message=user_input):
        # This catches the 'Polling for data' type messages from Bright Data
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    # Print a snippet of the progress/thinking
                    print(f"   (Progress): {part.text[:80]}...")
        
        if event.is_final_response() and event.content and event.content.parts:
            final_text = "".join([p.text for p in event.content.parts if p.text])
            
    return final_text

async def main():
    # 2. Setup Agent with verified tools
    model = LiteLlm(model="openai/gpt-5")
    agent = LlmAgent(
        name="LinkedIn_Direct_Scraper",
        model=model,
        instruction="Extract detailed LinkedIn data using 'web_data_linkedin_person_profile'.",
        tools=[MCPToolset(connection_params=StreamableHTTPServerParams(url=BRIGHTDATA_URL))]
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="sutd_final", session_service=session_service)
    session = await session_service.create_session(app_name="sutd_final", user_id="user")

    all_data = []

    # 3. Execution Loop
    print(f"🚀 Starting scrape for {len(target_urls)} LinkedIn profiles...")
    
    for url in target_urls:
        try:
            result = await scrape_profile(runner, session.id, url)
            
            print(f"✅ [Completed]: {url}")
            all_data.append({"url": url, "summary": result})
            
            # Incremental save to JSON
            with open("sutd_linkedin_profiles.json", "w") as f:
                json.dump(all_data, f, indent=4)
                
        except Exception as e:
            print(f"❌ [Failed]: {url} | Error: {e}")

    print("\n✨ All profiles processed. Results saved in 'sutd_linkedin_profiles.json'.")

if __name__ == "__main__":
    asyncio.run(main())