import requests
from bs4 import BeautifulSoup
import re
import urllib3
urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r = requests.get("https://www.studyinkorea.go.kr/ko/main.do", headers=headers, timeout=10, verify=False)
soup = BeautifulSoup(r.content, "html.parser")

links = soup.find_all("a", href=True)
print(f"Total links on Study in Korea main page: {len(links)}")

scholarship_links = []
for a in links:
    href = a["href"]
    text = a.get_text(strip=True)
    if "scholarship" in href.lower() or "gks" in href.lower() or "장학" in text or "gks" in text.lower():
        scholarship_links.append((text, href))

print(f"Found {len(scholarship_links)} scholarship-related links:")
for t, h in scholarship_links:
    print(f"  * {t} -> {h}")
