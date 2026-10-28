import cloudscraper
from bs4 import BeautifulSoup
import re
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
sitemap_url = "https://www.scholars4dev.com/post-sitemap.xml"
resp = scraper.get(sitemap_url, timeout=20)
soup = BeautifulSoup(resp.text, "xml")
urls = [loc.text for loc in soup.find_all("loc")]

# Filter specific scholarship articles (not listicles)
# Exclude listicles and general guides
listicle_keywords = [
    "top-", "scholarships-in-", "fully-funded-scholarships", "free-tuition", 
    "list-of-", "scholarships-for-", "tips", "resources-online", 
    "am-i-qualified", "hello-world", "merit-based-scholarships", "fellowships-in-usa"
]

specific_urls = []
for u in urls:
    slug = u.split("/")[-2] if u.endswith("/") else u.split("/")[-1]
    if not any(k in slug.lower() for k in listicle_keywords):
        if "/20" in u:
            specific_urls.append(u)

# Sort from newest to oldest
specific_urls.reverse()
print(f"Total specific scholarship URLs found: {len(specific_urls)}")
print("Sample first 15 newest specific scholarships:")
for u in specific_urls[:15]:
    print(u)
