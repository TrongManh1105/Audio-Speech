import cloudscraper
from bs4 import BeautifulSoup
import sys
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

scraper = cloudscraper.create_scraper()
r = scraper.get("https://www.youthop.com/scholarships")
soup = BeautifulSoup(r.text, "html.parser")

print("Page Title:", soup.title.text if soup.title else "")

# Find all opportunity titles and links
articles = soup.find_all("article")
if not articles:
    # Try finding divs that represent cards
    articles = soup.find_all("div", class_=re.compile(r"opportunity|post|card|item", re.I))

print(f"Total article containers found: {len(articles)}")

real_items = []
# Find links with h2, h3, h4 or titles
for a in soup.find_all("a", href=True):
    href = a["href"]
    title = a.get_text(strip=True)
    if "youthop.com/scholarships/" in href and len(title) > 20 and not href.endswith("/scholarships/"):
        real_items.append((title, href))

# Deduplicate
seen = set()
dedup = []
for t, h in real_items:
    if h not in seen:
        seen.add(h)
        dedup.append((t, h))

print(f"\nExtracted {len(dedup)} REAL LIVE scholarship articles from Youth Opportunities:")
for idx, (t, h) in enumerate(dedup[:10], start=1):
    print(f"[{idx}] {t}")
    print(f"    Link: {h}")
