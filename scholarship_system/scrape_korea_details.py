import requests
from bs4 import BeautifulSoup
import urllib3
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

urllib3.disable_warnings()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

r = requests.get("https://www.studyinkorea.go.kr/en/plan/scholarship.do", headers=headers, timeout=15, verify=False)
soup = BeautifulSoup(r.content, "html.parser")

# Find all tables or content boxes
tables = soup.find_all("table")
print(f"Total tables on GKS Plan page: {len(tables)}")
for idx, tbl in enumerate(tables, start=1):
    caption = tbl.find("caption")
    cap_text = caption.get_text(strip=True) if caption else "No caption"
    rows = tbl.find_all("tr")
    print(f"\n--- Table {idx}: {cap_text} ({len(rows)} rows) ---")
    for row in rows[:4]:
        cells = [c.get_text(separator=" ", strip=True) for c in row.find_all(["th", "td"])]
        print("   ", cells)

# Find tabs: gks-tab1, gks-tab2, etc.
tab_links = soup.find_all("a", href=lambda h: h and "tab=" in h)
print(f"\nFound {len(tab_links)} tab links on page:")
for tl in tab_links:
    print("  *", tl.get_text(strip=True), "->", tl["href"])
