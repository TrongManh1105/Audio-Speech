import requests
from bs4 import BeautifulSoup
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

url = "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

r = requests.get(url, headers=headers, timeout=15)
soup = BeautifulSoup(r.content, "html.parser")

print("STATUS CODE:", r.status_code)
print("TITLE:", soup.find("h1").get_text(strip=True) if soup.find("h1") else soup.title.text)

# Content area in scholars4dev
content = soup.find("div", class_="entry") or soup.find("div", class_="post_content") or soup.find("article")

if content:
    # Print all paragraphs / sections
    print("\n--- FULL ARTICLE CONTENT & SECTIONS ---\n")
    for elem in content.children:
        text = elem.get_text(separator=" ", strip=True) if hasattr(elem, "get_text") else str(elem).strip()
        if text:
            print(text)
            print("-" * 40)
else:
    print("Could not find content container.")
