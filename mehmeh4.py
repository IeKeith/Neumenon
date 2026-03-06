import json
import openai
import os

# Configuration
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure your API key is set in the environment variables
INPUT_FILE = "linkedin_profiles_cleaned.json"
OUTPUT_FILE = "linkedin_profiles_refined_2.json"

def refine_technical_description(title, description):
    """
    Transforms descriptions into a 3rd-person technical narrative.
    Maintains academic context (modules/classes) but focuses on strong points.
    """
    if not description or len(description) < 5:
        return description

    prompt = f"""
    Project Title: {title}
    Original Description: {description}

    Rewrite this into a concise 2-3 sentence technical summary.
    
    Constraints:
    1. Use THIRD-PERSON perspective only (e.g., "The project implements...", "The system utilizes...").
    2. Focus purely on the technical strong points, frameworks, and the problem solved.
    3. You MAY mention if it was a module, class, or assignment, but keep it brief.
    4. Start directly with the technical core of the project.
    5. Avoid personal pronouns (no "I", "me", "my", "we", "our").

    Refined Technical Description:
    """

    response = openai.chat.completions.create(
        model="gpt-4o", 
        messages=[
            {"role": "system", "content": "You are a technical editor for a university research portfolio."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1 
    )

    return response.choices[0].message.content.strip()

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    total_projects = sum(len(s.get("projects", [])) for s in data)
    current_count = 0

    for student in data:
        print(f"Processing projects for {student.get('name', 'Unknown')}...")
        
        for project in student.get("projects", []):
            current_count += 1
            title = project.get("title", "Untitled")
            original_desc = project.get("description", "")
            
            # Refine the description
            refined = refine_technical_description(title, original_desc)
            project["description"] = refined
            
            print(f"  [{current_count}/{total_projects}] Refined: {title[:40]}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    print(f"\nSuccess! Cleaned narrative data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()