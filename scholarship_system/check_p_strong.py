import cloudscraper
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
url = "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/"
r = scraper.get(url, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
entry = soup.find("div", class_="entry")

# Let's inspect the paragraphs in entry
for p in entry.find_all("p"):
    strong = p.find("strong")
    if strong:
        header = strong.get_text(strip=True)
        # remove the strong text to see what remains in p
        strong_text = strong.get_text()
        p_text = p.get_text(strip=True)
        content = p_text[len(header):].strip()
        print(f"[{header}] => {content[:100]}...")
