import pandas as pd

def convert_with_pandas(csv_file_path, json_file_path):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Orient='records' creates a list of dictionaries (standard JSON format)
    df.to_json(json_file_path, orient='records', indent=4)

# Usage
convert_with_pandas('linkedin_profiles_processed.csv', 'linkedin_profiles_processed.json')