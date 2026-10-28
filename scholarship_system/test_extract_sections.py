import cloudscraper
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

test_urls = [
    "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/",
    "https://www.scholars4dev.com/2026/10/21/chalmers-ipoet-scholarships-for-international-students/",
    "https://www.scholars4dev.com/2026/10/21/masters-scholarships-for-non-eu-students-at-university-of-twente/",
    "https://www.scholars4dev.com/2026/10/06/ens-international-selection-scholarships/",
    "https://www.scholars4dev.com/2026/09/24/clarendon-scholarships-at-university-of-oxford/",
    "https://www.scholars4dev.com/2026/08/24/eth-zurich-excellence-masters-scholarship-program/",
    "https://www.scholars4dev.com/2026/08/24/gates-scholarships-for-international-students-at-university-of-cambridge/",
    "https://www.scholars4dev.com/2026/09/07/tu-delft-excellence-scholarships-for-international-students/"
]

scraper = cloudscraper.create_scraper()

for url in test_urls:
    resp = scraper.get(url, timeout=20)
    if resp.status_code != 200:
        continue
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No title"
    entry = soup.find("div", class_="entry")
    
    # Extract deadline and number of scholarships
    text = entry.get_text("\n", strip=True) if entry else ""
    
    # Find Number of scholarships
    num_match = re.search(r"Number of Scholarships?:\s*(.*?)(?=\n[A-Z][a-zA-Z\s\(\)/]+:|\Z)", text, re.DOTALL)
    num_schol = num_match.group(1).strip() if num_match else "NOT FOUND"
    
    # Find Deadline
    dead_match = re.search(r"Deadline:\s*(.*?)(?=\n[A-Z][a-zA-Z\s\(\)/]+:|\Z)", text, re.DOTALL)
    dead_line = dead_match.group(1).strip() if dead_match else "NOT FOUND"
    
    # Find Host institution
    host_match = re.search(r"Host Institution\(s\):\s*(.*?)(?=\n[A-Z][a-zA-Z\s\(\)/]+:|\Z)", text, re.DOTALL)
    host = host_match.group(1).strip() if host_match else "NOT FOUND"
    
    print(f"=== {title} ===")
    print("Host:", host)
    print("Deadline:", dead_line)
    print("Number of Scholarships:\n", num_schol)
    print("-" * 50)
