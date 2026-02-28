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

# 1. Configuration
os.environ["OPENAI_API_KEY"] = "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"
BRIGHTDATA_TOKEN = "e47c0c51-175e-4f9a-90ca-974cc3a60f21"
BRIGHTDATA_URL = f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_TOKEN}&groups=advanced_scraping,social"

student_names = [
    "Teo Shao Tian", "Ngiam Ju Jin Lucas", "Benjamin Chong Mun Choen",
    "Thet Naung Oo @ Chi Jia Cai", "Naomi Marcelle Bachtiar", "Ong Jin Yang Brandon",
    "Chia Xujie Xavier", "Ian Phillip Lowe Heng Hang", "Ang You Shan",
    "Brandon Joseph Lawrence", "Chen Yueyi", "Louth Bin Rawshan",
    "Loy Yong Yi Wendy", "Lee Xue’En Esther", "Han Rui Ting", "Yong Hua Bing",
    "Ng Sin Jinn Ryan", "Loh Zheng Yi", "Adarsh Jayant Kamdar", "Voon Soo Jun",
    "Zhou Zhi", "Addison Chew Jun Wei", "Jeremia Juanputra", "Shuai Shuai",
    "Wu Tianyu", "Chiang Aiting Faye", "Woo Jiale Gerald", "Chia Yi Qing Eugene",
    "Tan Jin Yan", "Dong Yuanjia", "Ashlyn Goh Er Xuan", "Tan Yi Xuan",
    "Chan Jun Wei", "Hong Pengfei", "Lu Jiankun", "Wang Tianduo",
    "Nashita Abd Tipusultan", "Guntaguli", "Vieri Vincent", "Glenn Chia Jin Wee",
    "Rachel Chua Jia Ying", "Loh Jian An Lionell"
]

async def scrape_single_student(runner, session_id, name):
    """Encapsulates the scraping logic for one student."""
    prompt = f"Find the LinkedIn profile for SUTD student '{name}' and scrape their current role and education."
    user_input = types.Content(role="user", parts=[types.Part(text=prompt)])
    
    result_text = ""
    async for event in runner.run_async(session_id=session_id, user_id="user", new_message=user_input):
        if event.is_final_response() and event.content and event.content.parts:
            # Flattening parts to avoid 'list' has no attribute 'text'
            result_text = "".join([p.text for p in event.content.parts if p.text])
    return result_text

async def main():
    # 2. Setup ADK Components
    model = LiteLlm(model="openai/gpt-4o")
    agent = LlmAgent(
        name="SUTD_Scraper",
        model=model,
        instruction="Use 'search_engine' to find URLs and 'social_linkedin_profile' to scrape.",
        tools=[MCPToolset(connection_params=StreamableHTTPServerParams(url=BRIGHTDATA_URL))]
    )
    
    session_service = InMemorySessionService()
    runner = Runner(agent=agent, app_name="sutd_full_scan", session_service=session_service)
    session = await session_service.create_session(app_name="sutd_full_scan", user_id="user")

    scraped_data = []

    # 3. Execution Loop
    print(f"🚀 Starting full scrape for {len(student_names)} students...")
    
    for name in student_names:
        print(f"🔍 Processing: {name}...")
        try:
            # We run each name in its own turn to isolate errors
            info = await scrape_single_student(runner, session.id, name)
            
            entry = {"name": name, "raw_info": info}
            scraped_data.append(entry)
            
            print(f"✅ Result for {name}: {info[:100]}...")
            
            # Incremental Save (Protects data if the script crashes)
            with open("sutd_students.json", "w") as f:
                json.dump(scraped_data, f, indent=4)
                
        except Exception as e:
            print(f"❌ Failed to scrape {name}: {e}")
            scraped_data.append({"name": name, "error": str(e)})

    print("\n✨ Scrape Complete! Data saved to 'sutd_students.json'")

if __name__ == "__main__":
    asyncio.run(main())