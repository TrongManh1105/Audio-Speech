import requests
from bs4 import BeautifulSoup
import re
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=10)
soup = BeautifulSoup(r.content, "html.parser")

print("Status:", r.status_code, "HTML Length:", len(r.text))

# Let's see what tags exist in body
body = soup.find("body")
if body:
    # Print the first 1000 characters of body text
    print("Body text sample:")
    print(body.get_text(separator=" ", strip=True)[:600])
    
    # Find all links
    links = body.find_all("a", href=True)
    print(f"\nTotal links in body: {len(links)}")
    for a in links[:15]:
        print("  -> href:", a["href"], "| text:", a.get_text(strip=True)[:50])
