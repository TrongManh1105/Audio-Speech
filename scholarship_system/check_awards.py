import cloudscraper
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()

for url in [
    "https://www.scholars4dev.com/2026/09/24/clarendon-scholarships-at-university-of-oxford/",
    "https://www.scholars4dev.com/2026/08/24/gates-scholarships-for-international-students-at-university-of-cambridge/"
]:
    resp = scraper.get(url, timeout=20)
    soup = BeautifulSoup(resp.text, "html.parser")
    entry = soup.find("div", class_="entry")
    text = entry.get_text("\n", strip=True) if entry else ""
    m = re.search(r"Number of (?:Scholarships|Awards):\s*(.*?)(?=\n[A-Z][a-zA-Z\s\(\)/]+:|\Z)", text, re.DOTALL)
    print(url)
    if m:
        print("Number of Awards:", m.group(1).strip())
    else:
        print("Not found")
    print()
