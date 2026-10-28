import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 1. Inspect Youth Opportunities Feed
print("=== 1. YOUTH OPPORTUNITIES FEED INSPECTION ===")
r_yo = requests.get("https://www.youthop.com/scholarships/feed", headers=headers, timeout=10)
soup_yo = BeautifulSoup(r_yo.content, "html.parser")
items = soup_yo.find_all("item")
print(f"Found {len(items)} LIVE items in YouthOp RSS feed!")
for item in items[:6]:
    title_elem = item.find("title")
    title = title_elem.get_text(strip=True) if title_elem else ""
    link_elem = item.find("link")
    # In RSS, link can be in link tag or guid
    link = link_elem.next_sibling.strip() if link_elem and link_elem.next_sibling else (link_elem.get_text(strip=True) if link_elem else "")
    if not link:
        guid = item.find("guid")
        link = guid.get_text(strip=True) if guid else ""
    print(f"  * [YouthOp Live] {title}")
    print(f"    Link: {link}")

# 2. Inspect YBOX HTML structure
print("\n=== 2. YBOX HTML INSPECTION ===")
r_yb = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=10)
soup = BeautifulSoup(r_yb.content, "html.parser")
# Find all a tags
links = soup.find_all("a", href=True)
ybox_articles = []
for a in links:
    href = a["href"]
    text = a.get_text(strip=True)
    if ("/hoc-bong/" in href or "/bai-viet/" in href or "/tuyen-dung/" in href) and len(text) > 20:
        if not href.endswith("/hoc-bong"):
            ybox_articles.append((text, href))

print(f"Found {len(ybox_articles)} candidate scholarship articles in Ybox HTML!")
for title, href in ybox_articles[:8]:
    print(f"  * [YBOX Live] {title}")
    print(f"    Link: {href}")
