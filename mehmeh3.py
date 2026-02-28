import json
import ast

def clean_linkedin_json(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    cleaned_data = []

    for entry in data:
        name = entry.get("name")
        projects_raw = entry.get("projects")
        
        # Convert the stringified list into a Python list
        # literal_eval is used because the string contains 'None' and single quotes
        try:
            projects_list = ast.literal_eval(projects_raw)
        except (ValueError, SyntaxError):
            # Fallback for empty or malformed strings
            projects_list = []

        # Filter out 'None' values and keep the full project dictionaries
        valid_projects = [p for p in projects_list if isinstance(p, dict)]
        
        cleaned_entry = {
            "name": name,
            "projects": valid_projects
        }
        cleaned_data.append(cleaned_entry)

    # Save the result as a standard, valid JSON file
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=4, ensure_ascii=False)

    print(f"Cleaned JSON saved to {output_filename}")

# Run the cleaning process
clean_linkedin_json('linkedin_profiles_processed.json', 'linkedin_profiles_cleaned.json')