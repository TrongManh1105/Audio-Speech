import requests
import json

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*"
}

ybox_tests = [
    "https://ybox.vn/rss",
    "https://ybox.vn/feed",
    "https://ybox.vn/hoc-bong/rss",
    "https://api.ybox.vn/api/v1/posts?category=hoc-bong",
    "https://api.ybox.vn/api/v1/posts/hoc-bong",
    "https://api.ybox.vn/api/v1/articles?category=hoc-bong",
    "https://api.ybox.vn/api/v1/scholarships",
    "https://ybox.vn/api/posts?category=hoc-bong",
    "https://ybox.vn/api/hoc-bong"
]

for url in ybox_tests:
    try:
        r = requests.get(url, headers=headers, timeout=5)
        print(f"{url} -> Status: {r.status_code}, Length: {len(r.text)}")
        if r.status_code == 200 and len(r.text) > 100:
            print("  Preview:", r.text[:200])
    except Exception as e:
        print(f"{url} -> Error: {e}")
