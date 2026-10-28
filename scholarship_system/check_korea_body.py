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
headers = {"User-Agent": "Mozilla/5.0"}
r = requests.get("https://www.studyinkorea.go.kr/en/plan/scholarship.do", headers=headers, timeout=10, verify=False)
soup = BeautifulSoup(r.content, "html.parser")

main = soup.find("main") or soup.find("div", id=lambda x: x and ("content" in x.lower() or "container" in x.lower()))
if main:
    print("Found main/container tag:", main.name, main.get("id"), main.get("class"))
    # Print headings and paragraphs
    for child in main.find_all(["h2", "h3", "h4", "p", "li", "div"]):
        t = child.get_text(separator=" ", strip=True)
        if len(t) > 30 and child.name in ["h2", "h3", "h4", "p", "li"]:
            print(f"[{child.name}] {t[:120]}")
else:
    print("No main container, searching body...")
    body = soup.find("body")
    for h in body.find_all(["h2", "h3", "h4"]):
        print(f"[{h.name}] {h.get_text(strip=True)}")
        # Next sibling
        sib = h.find_next_sibling()
        if sib:
            print("   ->", sib.get_text(separator=" ", strip=True)[:150])
