import cloudscraper
from bs4 import BeautifulSoup
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()

urls_to_test = [
    "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/",
    "https://www.scholars4dev.com/2026/10/21/cambridge-international-scholarship-scheme-ciss/",
    "https://www.scholars4dev.com/2026/10/06/ens-international-selection-scholarships/",
    "https://www.scholars4dev.com/2026/10/06/vu-university-amsterdam-fellowship-programme-for-international-students/",
    "https://www.scholars4dev.com/2026/10/06/adlerbert-study-scholarships-at-chalmers-university-of-technology/",
    "https://www.scholars4dev.com/2026/09/24/clarendon-scholarships-at-university-of-oxford/",
    "https://www.scholars4dev.com/2026/09/24/weidenfeld-scholarships-at-university-of-oxford/",
    "https://www.scholars4dev.com/2026/09/24/ilot-scholarships-at-university-of-british-columbia/",
    "https://www.scholars4dev.com/2026/09/07/british-chevening-scholarships/",
    "https://www.scholars4dev.com/2026/09/07/kth-tuition-fee-waivers-for-non-eu-students/",
    "https://www.scholars4dev.com/2026/08/24/eth-zurich-excellence-masters-scholarship-program/",
    "https://www.scholars4dev.com/2026/07/29/epfl-excellence-fellowships/",
    "https://www.scholars4dev.com/2026/07/13/knight-hennessy-scholars-at-stanford-university/",
    "https://www.scholars4dev.com/2026/07/13/lester-b-pearson-international-scholarship-program-at-university-of-toronto/"
]

def parse_post(url):
    try:
        r = scraper.get(url, timeout=15)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        title = soup.find("h1").get_text(strip=True) if soup.find("h1") else "No title"
        entry = soup.find("div", class_="entry") or soup.find("article")
        if not entry:
            return None
        text = entry.get_text("\n", strip=True)
        
        # Deadline
        dl_match = re.search(r"Deadline:\s*(.*?)(?=\n(?:Study in|Course starts|Brief description):|\n\n|\Z)", text, re.I | re.DOTALL)
        deadline = dl_match.group(1).replace("\n", " ").strip() if dl_match else "N/A"
        
        # Study in
        st_match = re.search(r"Study in:\s*(.*?)(?=\n(?:Course starts|Brief description|Deadline):|\n\n|\Z)", text, re.I | re.DOTALL)
        study_in = st_match.group(1).replace("\n", " ").strip() if st_match else "N/A"
        
        # Host Institution
        host_match = re.search(r"Host Institution\(s\):\s*(.*?)(?=\n(?:Field\(s\) of study|Level/Field of study|Number of):|\n\n|\Z)", text, re.I | re.DOTALL)
        host = host_match.group(1).replace("\n", " ").strip() if host_match else "N/A"
        
        # Number of scholarships
        num_match = re.search(r"Number of (?:Scholarships|Awards):\s*(.*?)(?=\n(?:Target group|Scholarship value|Eligibility):|\n\n|\Z)", text, re.I | re.DOTALL)
        num_schol = num_match.group(1).replace("\n", " ").strip() if num_match else "N/A"
        
        return {
            "title": title,
            "host": host,
            "deadline": deadline,
            "study_in": study_in,
            "num_scholarships": num_schol
        }
    except Exception as e:
        return {"error": str(e)}

for u in urls_to_test:
    res = parse_post(u)
    if res:
        print(f"Title: {res['title']}")
        print(f"  Host: {res['host']}")
        print(f"  Country: {res['study_in']}")
        print(f"  Deadline: {res['deadline']}")
        print(f"  Quota: {res['num_scholarships']}")
        print()
