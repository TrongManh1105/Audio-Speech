import cloudscraper
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
url = "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/"
r = scraper.get(url, timeout=15)
soup = BeautifulSoup(r.text, "html.parser")
entry = soup.find("div", class_="entry")

sections = {}
current_sec = "header_info"
sections[current_sec] = []

KNOWN_HEADERS = [
    "deadline", "study in", "course starts", "brief description",
    "host institution", "field(s) of study", "level/field", "number of scholarships",
    "number of awards", "target group", "scholarship value", "eligibility",
    "application instructions", "website"
]

for child in entry.children:
    if not child.name:
        continue
    text = child.get_text(separator="\n", strip=True)
    if not text:
        continue
    
    # check if child is a header
    matched_header = None
    first_line = text.split("\n")[0].strip().lower().rstrip(":")
    for kh in KNOWN_HEADERS:
        if first_line.startswith(kh) or kh in first_line:
            matched_header = kh
            break
            
    if matched_header:
        current_sec = matched_header
        if current_sec not in sections:
            sections[current_sec] = []
        # if there is content after header on the same block
        rem = text[len(first_line):].lstrip(":").strip()
        if rem:
            sections[current_sec].append(rem)
    else:
        sections[current_sec].append(text)

print("Parsed sections:")
for k, v in sections.items():
    content = " | ".join(v)
    print(f"=== {k.upper()} ===")
    print(content[:300])
    print()
