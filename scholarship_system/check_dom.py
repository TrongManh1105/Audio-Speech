import requests
from bs4 import BeautifulSoup
import re

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

print("=== 1. YouthOp HTML Title & Cards ===")
r_yo = requests.get("https://www.youthop.com/scholarships", headers=headers, timeout=10)
soup_yo = BeautifulSoup(r_yo.content, "html.parser")
print("YouthOp Title:", soup_yo.title.text if soup_yo.title else "No title")
cards = soup_yo.find_all(class_=re.compile(r"card|post|item|opportunity", re.I))
print("YouthOp Cards found:", len(cards))
for c in cards[:5]:
    print("  -> Class:", c.get("class"), "Text:", c.get_text(separator=" ", strip=True)[:100])

print("\n=== 2. YBOX HTML Title & Links ===")
r_yb = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=10)
soup_yb = BeautifulSoup(r_yb.content, "html.parser")
print("Ybox Title:", soup_yb.title.text if soup_yb.title else "No title")
# Check if React SPA
scripts = soup_yb.find_all("script")
print("Ybox Scripts count:", len(scripts))
# Search for window.__INITIAL_STATE__ or json
for s in scripts:
    if s.string and ("scholarship" in s.string or "post" in s.string or "hoc-bong" in s.string or "__INITIAL_STATE__" in s.string):
        print("Found state script in Ybox! Length:", len(s.string))
