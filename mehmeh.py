import requests
import time
import json
API_KEY = "180a2d70-1698-4f30-8d3f-b4fb20f949a0"
DATASET_ID = "gd_l1viktl72bvl7bjuj0"  # LinkedIn Profiles dataset id

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

target_urls = [
    "https://sg.linkedin.com/in/ray-lai-627aaa239",
    "https://sg.linkedin.com/in/gabriel-kay-a76039240",
    "https://sg.linkedin.com/in/dhyeya-anand-b839b2266",
    "https://sg.linkedin.com/in/adikum",
    "https://sg.linkedin.com/in/ayra-mohammed-a920742a3",
    "https://sg.linkedin.com/in/kelliesim",
    "https://sg.linkedin.com/in/shuenn-yuen-han-60a467261",
    "https://sg.linkedin.com/in/anna-rica-sawit",
    "https://sg.linkedin.com/in/jatlysonang",
]

inputs = [{"url": u} for u in target_urls]

# 1) Trigger
trigger_resp = requests.post(
    "https://api.brightdata.com/datasets/v3/trigger",
    params={"dataset_id": DATASET_ID, "format": "json"},
    headers=headers,
    json=inputs,
)
trigger_resp.raise_for_status()
snapshot_id = trigger_resp.json()["snapshot_id"]
print("Triggered snapshot:", snapshot_id)

# 2) Poll STATUS endpoint (no ?format=json here)
while True:
    status_resp = requests.get(
        f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}",
        headers=headers,
    )
    status_resp.raise_for_status()

    try:
        status_data = status_resp.json()
    except json.JSONDecodeError:
        print("Status response is not JSON, raw content:")
        print(status_resp.text[:1000])
        raise

    status = status_data.get("status")
    print("Status:", status)

    if status == "ready":
        break
    if status == "failed":
        raise RuntimeError("Scrape failed")

    time.sleep(5)

# 3) Download results
download_resp = requests.get(
    f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json",
    headers=headers,
)
download_resp.raise_for_status()

# First try: JSON array
try:
    results = download_resp.json()
except json.JSONDecodeError:
    # Fallback: JSON Lines (one JSON object per line)
    text = download_resp.text
    lines = [line for line in text.splitlines() if line.strip()]
    results = [json.loads(line) for line in lines]

print(f"Got {len(results)} profiles")
for r in results:
    print(r.get("name"), "-", r.get("current_company", {}).get("name"))