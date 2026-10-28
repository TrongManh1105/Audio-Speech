import requests
import json
import urllib3
urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

print("--- 1. Testing Scholars4dev ---")
try:
    r = requests.get("https://www.scholars4dev.com/category/scholarships-list/", headers=headers, timeout=10)
    print("Scholars4dev status:", r.status_code, "Length:", len(r.text))
except Exception as e:
    print("Scholars4dev error:", e)

print("\n--- 2. Testing Youth Opportunities (HTML & Feed & API) ---")
for url in ["https://www.youthop.com/scholarships", "https://www.youthop.com/feed", "https://www.youthop.com/scholarships/feed"]:
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"YouthOp {url} -> Status: {r.status_code}, Length: {len(r.text)}")
    except Exception as e:
        print(f"YouthOp {url} -> Error: {e}")

print("\n--- 3. Testing Chevening ---")
try:
    r = requests.get("https://www.chevening.org/scholarships/", headers=headers, timeout=8)
    print("Chevening status:", r.status_code, "Length:", len(r.text))
except Exception as e:
    print("Chevening error:", e)

print("\n--- 4. Testing Ybox ---")
for url in ["https://ybox.vn/hoc-bong", "https://api.ybox.vn/api/posts?category=hoc-bong"]:
    try:
        r = requests.get(url, headers=headers, timeout=8)
        print(f"Ybox {url} -> Status: {r.status_code}, Length: {len(r.text)}")
    except Exception as e:
        print(f"Ybox {url} -> Error: {e}")

print("\n--- 5. Testing Study in Korea ---")
for url in ["https://www.studyinkorea.go.kr/en/scholarship/GksScholarship.do", "https://www.studyinkorea.go.kr/ko/main.do"]:
    try:
        r = requests.get(url, headers=headers, timeout=8, verify=False)
        print(f"Study in Korea {url} -> Status: {r.status_code}, Length: {len(r.text)}")
    except Exception as e:
        print(f"Study in Korea {url} -> Error: {e}")
