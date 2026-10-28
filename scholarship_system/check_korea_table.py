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

# 1. Fetch Scholarship Notices (Thông báo học bổng chính phủ & trường)
notice_url = "https://www.studyinkorea.go.kr/en/notice/scholarshipsList.do?boardSort=3"
print(f"[*] Fetching notices from: {notice_url}")
r = requests.get(notice_url, headers=headers, timeout=10, verify=False)
soup = BeautifulSoup(r.content, "html.parser")

table = soup.find("table")
if table:
    rows = table.find_all("tr")
    print(f"Found table with {len(rows)} rows!")
    for row in rows[:8]:
        cols = [c.get_text(strip=True) for c in row.find_all(["th", "td"])]
        a = row.find("a")
        link = a["href"] if a and a.has_attr("href") else ""
        print("  Row:", cols, "Link:", link)
else:
    print("No table found, checking list items...")
    items = soup.select(".list-item, .board-list, .notice-item, li")
    print("Found items:", len(items))

# 2. Fetch GKS Plan page
plan_url = "https://www.studyinkorea.go.kr/en/plan/scholarship.do"
print(f"\n[*] Fetching GKS Plan from: {plan_url}")
r_plan = requests.get(plan_url, headers=headers, timeout=10, verify=False)
soup_plan = BeautifulSoup(r_plan.content, "html.parser")
print("Plan page title:", soup_plan.title.text if soup_plan.title else "")
tabs = soup_plan.select(".tab-content, .gks-tab, .scholarship-info, h3, h4")
print("Headings found in GKS Plan:", [h.get_text(strip=True) for h in tabs if h.name in ['h3', 'h4']][:8])
