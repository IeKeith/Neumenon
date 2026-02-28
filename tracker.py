import requests

url = "https://api.brightdata.com/datasets/v3/progress/sd_mm5u9qbsmajpshco1"

headers = {"Authorization": "Bearer e47c0c51-175e-4f9a-90ca-974cc3a60f21"}

response = requests.get(url, headers=headers)

print(response.text)