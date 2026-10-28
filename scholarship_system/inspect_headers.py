import cloudscraper
from bs4 import BeautifulSoup
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
    print(f"=== {url} ===")
    strongs = entry.find_all("strong") if entry else []
    for s in strongs:
        print("Strong:", s.get_text(strip=True))
    print()
