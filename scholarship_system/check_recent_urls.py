import cloudscraper
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
sitemap_url = "https://www.scholars4dev.com/post-sitemap.xml"
resp = scraper.get(sitemap_url, timeout=20)
soup = BeautifulSoup(resp.text, "xml")
urls = [loc.text for loc in soup.find_all("loc")]

recent_urls = [u for u in urls if "/202" in u]
print(f"Total URLs from 2020+: {len(recent_urls)}")
for u in recent_urls[-30:]:
    print(u)
