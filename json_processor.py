import json
import pandas as pd

def load_linkedin_data(file_path):
    """Loads JSON Lines data into a list of dictionaries."""
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip(): 
                data.append(json.loads(line))
    return data

def process_and_analyze(data):
    """Processes the raw list of dicts into a DataFrame and prints analytics."""
    df = pd.DataFrame(data)
    df.to_csv('linkedin_profiles_processed.csv', index=False)  # Save raw data for reference
    print(df.head())
    # 1. Feature Extraction: Clean and count nested data
    # Count the number of valid projects per user
    df['num_projects'] = df['projects'].apply(
        lambda x: len([p for p in x if p is not None]) if isinstance(x, list) else 0
    )
    
    # Count the number of certifications per user
    df['num_certifications'] = df['certifications'].apply(
        lambda x: len(x) if isinstance(x, list) else 0
    )
    
    # Extract the user's primary school name (if available)
    df['primary_school'] = df['education'].apply(
        lambda x: x.get('title', 'Unknown') if isinstance(x, list) and len(x) > 0 else 'Unknown'
    )

    # 2. General Dataset Statistics
    print("=== DATASET OVERVIEW ===")
    print(f"Total Profiles Analyzed: {len(df)}")
    
    print("\n=== NETWORK METRICS (Averages) ===")
    print(f"Average Followers: {df['followers'].mean():.1f}")
    print(f"Average Connections: {df['connections'].mean():.1f}")

    # 3. Categorical Insights
    print("\n=== MOST COMMON UNIVERSITIES ===")
    print(df['primary_school'].value_counts().head(5).to_string())

    print("\n=== CURRENT COMPANIES ===")
    # Fill missing companies with 'None listed' to avoid blank prints
    companies = df['current_company_name'].fillna('None listed')
    print(companies.value_counts().head(5).to_string())

    # 4. Individual Profile Performance Matrix
    print("\n=== PROFILE PERFORMANCE RANKING (By Followers) ===")
    metrics_df = df[['name', 'followers', 'connections', 'num_projects', 'num_certifications']]
    sorted_metrics = metrics_df.sort_values(by='followers', ascending=False).reset_index(drop=True)
    print(sorted_metrics.to_string())

# Main execution
file_path = 'linkedin_profiles2 copy.json'
raw_data = load_linkedin_data(file_path)
process_and_analyze(raw_data)