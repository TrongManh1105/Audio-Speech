import requests
import json

url = "https://www.chevening.org/wp-json/wp/v2/pages/1580"
headers = {"User-Agent": "Mozilla/5.0"}

try:
    r = requests.get(url, headers=headers, timeout=10)
    print("Chevening WP API status:", r.status_code)
    data = r.json()
    print("Title:", data.get("title", {}).get("rendered"))
    content = data.get("content", {}).get("rendered", "")
    print("Content length:", len(content))
    print("Snippet:", content[:300])
except Exception as e:
    print("Error:", e)
