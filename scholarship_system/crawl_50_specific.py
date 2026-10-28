import cloudscraper
from bs4 import BeautifulSoup
import re
import sys
import json
import time

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

scraper = cloudscraper.create_scraper()
sitemap_url = "https://www.scholars4dev.com/post-sitemap.xml"
resp = scraper.get(sitemap_url, timeout=20)
soup = BeautifulSoup(resp.text, "xml")
urls = [loc.text for loc in soup.find_all("loc")]

listicle_keywords = [
    "top-", "scholarships-in-", "fully-funded-scholarships", "free-tuition", 
    "list-of-", "scholarships-for-", "tips", "resources-online", 
    "am-i-qualified", "hello-world", "merit-based-scholarships", "fellowships-in-usa",
    "distance-learning", "europe-scholarships", "tuition-scholarships"
]

specific_urls = []
for u in urls:
    slug = u.split("/")[-2] if u.endswith("/") else u.split("/")[-1]
    if not any(k in slug.lower() for k in listicle_keywords):
        if "/20" in u:
            specific_urls.append(u)

specific_urls.reverse()
print(f"Total specific URLs available: {len(specific_urls)}")

# Ensure Gothenburg is first
gothenburg_url = "https://www.scholars4dev.com/2026/10/21/the-university-of-gothenburg-study-scholarship/"
if gothenburg_url in specific_urls:
    specific_urls.remove(gothenburg_url)
specific_urls.insert(0, gothenburg_url)

KNOWN_HEADERS = [
    ("deadline", "Deadline:"),
    ("study in", "Study in:"),
    ("course starts", "Course starts:"),
    ("brief description", "Brief description:"),
    ("host institution", "Host Institution(s):"),
    ("level/field of study", "Level/Field(s) of study:"),
    ("field(s) of study", "Field(s) of study:"),
    ("number of scholarships", "Number of Scholarships:"),
    ("number of awards", "Number of Awards:"),
    ("target group", "Target group:"),
    ("scholarship value", "Scholarship value/inclusions:"),
    ("eligibility", "Eligibility:"),
    ("application instructions", "Application instructions:"),
    ("website", "Website:")
]

def parse_post(url):
    try:
        r = scraper.get(url, timeout=12)
        if r.status_code != 200:
            return None
        s = BeautifulSoup(r.text, "html.parser")
        title_el = s.find("h1")
        title = title_el.get_text(strip=True) if title_el else ""
        entry = s.find("div", class_="entry") or s.find("article")
        if not entry:
            return None
            
        sections = {"header_info": []}
        current_sec = "header_info"
        
        for child in entry.children:
            if not child.name:
                continue
            text = child.get_text(separator="\n", strip=True)
            if not text:
                continue
            
            matched = None
            first_line = text.split("\n")[0].strip().lower().rstrip(":")
            for key, orig_name in KNOWN_HEADERS:
                if first_line.startswith(key) or key in first_line:
                    matched = key
                    break
            
            if matched:
                current_sec = matched
                if current_sec not in sections:
                    sections[current_sec] = []
                rem = text[len(first_line):].lstrip(":").strip()
                if rem:
                    sections[current_sec].append(rem)
            else:
                if current_sec not in sections:
                    sections[current_sec] = []
                sections[current_sec].append(text)
                
        def get_sec(*keys):
            for k in keys:
                if k in sections and sections[k]:
                    return " \n".join(sections[k]).strip()
            return ""
            
        header_text = " \n".join(sections.get("header_info", []))
        
        dl = get_sec("deadline")
        if not dl:
            m = re.search(r"Deadline:\s*([^\n\r]+)", header_text, re.I)
            if m: dl = m.group(1).strip()
            
        study_in = get_sec("study in")
        if not study_in:
            m = re.search(r"Study in:\s*([^\n\r]+)", header_text, re.I)
            if m: study_in = m.group(1).strip()
            
        degree = "Masters Degree"
        hl = header_text.lower()
        if "master" in hl and "bachelor" in hl:
            degree = "Masters / Bachelors"
        elif "bachelor" in hl or "undergraduate" in hl:
            degree = "Bachelors Degree"
        elif "phd" in hl or "doctoral" in hl:
            degree = "PhD / Doctoral"
        elif "master" in hl:
            degree = "Masters Degree"
            
        quota = get_sec("number of scholarships", "number of awards")
        brief = get_sec("brief description")
        host = get_sec("host institution")
        fields = get_sec("field(s) of study", "level/field of study")
        target = get_sec("target group")
        value = get_sec("scholarship value")
        eligibility = get_sec("eligibility")
        app_inst = get_sec("application instructions")
        
        # Clean clean strings
        return {
            "title": title,
            "brief": brief,
            "host": host,
            "fields": fields,
            "quota": quota,
            "target": target,
            "value": value,
            "eligibility": eligibility,
            "app_instructions": app_inst,
            "deadline": dl,
            "study_in": study_in,
            "degree": degree,
            "url": url
        }
    except Exception as e:
        return None

results = []
# Crawl up to 50 specific scholarships
target_count = 50
print(f"Scraping up to {target_count} specific individual scholarships...")

for i, u in enumerate(specific_urls[:target_count]):
    item = parse_post(u)
    if item and item["title"] and item["host"]:
        results.append(item)
        print(f"[{len(results)}] {item['title'][:45]} | Q: {item['quota'][:30]} | DL: {item['deadline'][:25]}")
    time.sleep(0.3)

with open("crawled_specific_scholars4dev.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n[✓] Saved {len(results)} detailed specific scholarships to crawled_specific_scholars4dev.json")
