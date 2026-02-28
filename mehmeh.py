import requests
import time
import json
API_KEY = "180a2d70-1698-4f30-8d3f-b4fb20f949a0"
DATASET_ID = "gd_l1viktl72bvl7bjuj0"  # LinkedIn Profiles dataset id

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
}

# === FULL LIST OF TARGET URLS (old + new) ===
target_urls = [
    # Old ones
    "https://sg.linkedin.com/in/ray-lai-627aaa239",
    "https://sg.linkedin.com/in/gabriel-kay-a76039240",
    "https://sg.linkedin.com/in/dhyeya-anand-b839b2266",
    "https://sg.linkedin.com/in/adikum",
    "https://sg.linkedin.com/in/ayra-mohammed-a920742a3",
    "https://sg.linkedin.com/in/kelliesim",
    "https://sg.linkedin.com/in/shuenn-yuen-han-60a467261",
    "https://sg.linkedin.com/in/anna-rica-sawit",
    "https://sg.linkedin.com/in/jatlysonang",

    # New ones you just sent
    "https://sg.linkedin.com/in/zhou-zhi-178851144",
    "https://sg.linkedin.com/in/jeremia-juanputra",
    "https://sg.linkedin.com/in/zheng-nan-ng-14787a12a",
    "https://jp.linkedin.com/in/susiwatita",
    "https://ch.linkedin.com/in/cshikai",
    "https://sg.linkedin.com/in/lam-yu-en",
    "https://sg.linkedin.com/in/tan-see-yen-amanda-50606b32b",
    "https://sg.linkedin.com/in/valerie-chua-yu-jia",
    "https://se.linkedin.com/in/cycraynard",
    "https://sg.linkedin.com/in/anirudh-bharadwaj-6b54a6217",
    "https://sg.linkedin.com/in/loh-jun-siang-928a0122b",
    "https://sg.linkedin.com/in/changsu-engineering",
    "https://sg.linkedin.com/in/clairetham",
    "https://sg.linkedin.com/in/yogesh-shelgaonkar",
    "https://sg.linkedin.com/in/sze-yin-yeo-159819221",
    "https://sg.linkedin.com/in/yuqing-jiang-b82007267",
    "https://sg.linkedin.com/in/limazib",
    "https://sg.linkedin.com/in/wong-yu-fei"
]

inputs = [{"url": u} for u in target_urls]

# === 1) Trigger the scrape ===
trigger_resp = requests.post(
    "https://api.brightdata.com/datasets/v3/trigger",
    params={"dataset_id": DATASET_ID, "format": "json"},
    headers=headers,
    json=inputs,
)
trigger_resp.raise_for_status()
snapshot_id = trigger_resp.json()["snapshot_id"]
print("Triggered snapshot:", snapshot_id)

# === 2) Poll status (no ?format=json here) ===
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

# === 3) Download results (may be JSON array or JSONL) ===
download_resp = requests.get(
    f"https://api.brightdata.com/datasets/v3/snapshot/{snapshot_id}?format=json",
    headers=headers,
)
download_resp.raise_for_status()
raw_text = download_resp.text

# Try JSON array/object first
try:
    data = json.loads(raw_text)
    if isinstance(data, list):
        records = data
    else:
        records = [data]
except json.JSONDecodeError:
    # Fallback: JSON Lines (one JSON object per line)
    lines = [line for line in raw_text.splitlines() if line.strip()]
    records = [json.loads(line) for line in lines]

print(f"Got {len(records)} profiles")

for r in records:
    name = r.get("name")
    cc = r.get("current_company") or {}
    company_name = cc.get("name") if isinstance(cc, dict) else None
    print(name, "-", company_name)

# === 4) Save to a DIFFERENT output file name ===
output_file = "linkedin_profiles_v2.jsonl"  # new file name
with open(output_file, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"Saved {len(records)} profiles to {output_file}")