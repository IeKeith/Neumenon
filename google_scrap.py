import asyncio
import os
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Credentials
os.environ["OPENAI_API_KEY"] = "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"
BRIGHTDATA_TOKEN = "e47c0c51-175e-4f9a-90ca-974cc3a60f21"
# We include both groups: 'advanced_scraping' to read the SUTD site, 
# and 'social' to scrape LinkedIn profiles.
BRIGHTDATA_URL = f"https://mcp.brightdata.com/mcp?token={BRIGHTDATA_TOKEN}&groups=advanced_scraping,social"

async def scrape_student_list():
    # 1. Initialize Model
    model = LiteLlm(model="openai/gpt-4o")

    # 2. Define the Agent
    # We give it clear instructions on how to handle SUTD student searches
    sutd_agent = LlmAgent(
        name="SUTD_Honours_Scraper",
        model=model,
        instruction="""
        You are a research assistant. 
        1. If a URL is provided, use 'web_data_generic_scraper' to extract student names.
        2. For each name, use 'search_engine' to find their LinkedIn profile.
        3. Use 'social_linkedin_profile' to extract their current role and skills.
        4. Focus on finding SUTD students specifically.
        """,
        tools=[
            MCPToolset(
                connection_params=StreamableHTTPServerParams(
                    url=BRIGHTDATA_URL,
                ),
            )
        ],
    )

    # 3. Setup Runner and Session
    session_service = InMemorySessionService()
    runner = Runner(
        agent=sutd_agent, 
        app_name="sutd_scraper", 
        session_service=session_service
    )
    session = await session_service.create_session(app_name="sutd_scraper", user_id="user_1")

    # 4. Define the Task
    # Option A: Use the URL
    sutd_url = "https://www.sutd.edu.sg/campus-life/student-life/student-awards/honours-list/all/"
    prompt = f"Visit this URL: {sutd_url}. Extract the names of the students and find the LinkedIn profiles for the first 3 names as a test."

    # Option B: (Uncomment to use your manual list instead)
    # manual_list = "Teo Shao Tian, Ngiam Ju Jin Lucas, Benjamin Chong Mun Choen..."
    # prompt = f"Find and scrape the LinkedIn profiles for these students: {manual_list[:500]}"

    user_input = types.Content(role="user", parts=[types.Part(text=prompt)])

    print("🚀 Starting the SUTD Honours scraping pipeline...")

    # 5. Execute with the correct list-part loop
    async for event in runner.run_async(session_id=session.id, user_id="user_1", new_message=user_input):
        if event.content and event.content.parts:
            for part in event.content.parts:
                # This check avoids the AttributeError by accessing .text on the PART, not the LIST
                if part.text:
                    print(f"DEBUG [Agent]: {part.text[:150]}...")
        
        if event.is_final_response() and event.content and event.content.parts:
            print("\n--- FINAL SUMMARY ---")
            # Correctly joining the text parts
            final_text = "".join([p.text for p in event.content.parts if p.text])
            print(final_text)

if __name__ == "__main__":
    asyncio.run(scrape_student_list())