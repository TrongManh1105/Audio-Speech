import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "close"
}

print("Testing direct request to Chevening...")
start = time.time()
try:
    # Use stream=True to avoid hanging on large bodies
    r = session.get("https://www.chevening.org/scholarships/", headers=headers, timeout=25, stream=True)
    print(f"Status: {r.status_code}, Elapsed: {time.time() - start:.2f}s")
    content = b""
    for chunk in r.iter_content(chunk_size=8192):
        content += chunk
        if len(content) > 50000:
            break
    print(f"Downloaded {len(content)} bytes successfully!")
    soup = BeautifulSoup(content, "html.parser")
    print("Page Title:", soup.title.text if soup.title else "")
    # Find links
    links = [a["href"] for a in soup.find_all("a", href=True) if "chevening.org" in a["href"]]
    print(f"Found {len(links)} Chevening links in downloaded chunk!")
    for l in links[:5]:
        print("  ->", l)
except Exception as e:
    print(f"Error ({time.time() - start:.2f}s):", e)
