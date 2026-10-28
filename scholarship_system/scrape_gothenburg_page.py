import cloudscraper
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

url = "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/"
scraper = cloudscraper.create_scraper()
resp = scraper.get(url, timeout=20)
print("Status:", resp.status_code)
soup = BeautifulSoup(resp.text, "html.parser")

entry = soup.find("div", class_="entry") or soup.find("article")
if entry:
    print(entry.get_text("\n", strip=True)[:3000])
else:
    print("Entry not found")
