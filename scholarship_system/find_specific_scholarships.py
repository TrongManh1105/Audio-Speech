import cloudscraper
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
sitemap_url = "https://www.scholars4dev.com/post-sitemap.xml"
resp = scraper.get(sitemap_url, timeout=20)
print("Sitemap status:", resp.status_code)

soup = BeautifulSoup(resp.text, "xml")
urls = [loc.text for loc in soup.find_all("loc")]
print(f"Total URLs in sitemap: {len(urls)}")

# Filter out listicles (Top 10, Top 20, etc.) vs specific individual scholarships
specific_scholarships = []
listicles = []

for u in urls:
    slug = u.split("/")[-2] if u.endswith("/") else u.split("/")[-1]
    if any(k in slug.lower() for k in ["top-", "scholarships-in-", "fully-funded-scholarships", "free-tuition", "list-of-", "scholarships-for-"]):
        listicles.append(u)
    else:
        specific_scholarships.append(u)

print(f"Specific scholarship URLs: {len(specific_scholarships)}")
print(f"Listicle URLs: {len(listicles)}")
print("\nSample 20 specific scholarship URLs:")
for u in specific_scholarships[:20]:
    print(u)
