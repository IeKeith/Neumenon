import requests
import json

API_KEY = "180a2d70-1698-4f30-8d3f-b4fb20f949a0"
SNAPSHOT_ID = "sd_mm60wbrm20ublz6zql"  # e.g. "s_maof15r7v28n4gc95"

headers = {
    "Authorization": f"Bearer {API_KEY}",
}

# 1) Call the snapshot download endpoint directly
#    We request ?format=json – this may return JSON array OR JSON Lines (multiple JSON objects)
url = f"https://api.brightdata.com/datasets/v3/snapshot/{SNAPSHOT_ID}?format=json"

resp = requests.get(url, headers=headers)
resp.raise_for_status()

raw_text = resp.text

# 2) Try to parse as a single JSON value (array or object)
try:
    data = json.loads(raw_text)
    # If it's a list, we already have all records
    if isinstance(data, list):
        records = data
    else:
        # Single object – wrap in list for consistency
        records = [data]
except json.JSONDecodeError:
    # 3) Fallback: treat as JSON Lines (one JSON object per line)
    lines = [line for line in raw_text.splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]

# 4) Use the parsed records
print(f"Got {len(records)} profiles")

for r in records:
    name = r.get("name")
    current_company = None
    cc = r.get("current_company") or {}
    if isinstance(cc, dict):
        current_company = cc.get("name")
    print(name, "-", current_company)

# Optional: save to file as JSON Lines
output_file = "linkedin_profiles.jsonl"
with open(output_file, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Saved {len(records)} profiles to {output_file}")
