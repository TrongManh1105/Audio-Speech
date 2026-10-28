import requests

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r1 = requests.get("https://www.youthop.com/scholarships/feed", headers=headers, timeout=10)
print("--- YouthOp Response snippet ---")
print(r1.text[:500])

r2 = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=10)
print("\n--- YBOX Response snippet ---")
print(r2.text[:500])
