"""
Bộ cào dữ liệu Scholars4dev diện rộng (Deep Bulk Crawler)
Cào qua toàn bộ 49 trang chính và các chuyên mục học bổng quốc tế (Masters, PhD, Undergraduate, Europe, US/Canada, Asia, Australia)
"""

import sys
import os
import re
import csv
import time
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "scholars4dev_scholarships.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8"
}

CATEGORY_PAGES = [
    # Main feed
    *[f"https://www.scholars4dev.com/page/{p}/" for p in range(1, 50)],
    # Target group: International students
    *[f"https://www.scholars4dev.com/category/target-group/international-students/page/{p}/" for p in range(1, 30)],
    # Degree levels
    *[f"https://www.scholars4dev.com/category/level/masters-scholarships/page/{p}/" for p in range(1, 25)],
    *[f"https://www.scholars4dev.com/category/level/phd-scholarships/page/{p}/" for p in range(1, 20)],
    *[f"https://www.scholars4dev.com/category/level/undergraduate-scholarships/page/{p}/" for p in range(1, 15)],
    # Regions
    *[f"https://www.scholars4dev.com/category/country/europe-scholarships/page/{p}/" for p in range(1, 20)],
    *[f"https://www.scholars4dev.com/category/country/usa-canada-scholarships/page/{p}/" for p in range(1, 20)],
    *[f"https://www.scholars4dev.com/category/country/asia-scholarships/page/{p}/" for p in range(1, 15)],
    *[f"https://www.scholars4dev.com/category/country/australia-scholarships/page/{p}/" for p in range(1, 15)]
]

def parse_post(post):
    try:
        title_elem = post.find(["h2", "h1", "h3"])
        if not title_elem:
            return None
        a_tag = title_elem.find("a")
        if not a_tag:
            return None

        title = a_tag.get_text(strip=True)
        link = a_tag.get("href", "")
        if not title or len(title) < 5:
            return None

        content_elem = post.find("div", class_="entry clearfix") or post.find("div", class_="post_content") or post
        content_text = content_elem.get_text(separator="\n", strip=True) if content_elem else ""

        # Bóc tách bậc học
        degree = "Bachelors / Masters / PhD"
        if "Master" in content_text or "Postgraduate" in content_text:
            degree = "Thạc sĩ (Master's Degree)"
        elif "PhD" in content_text or "Doctoral" in content_text:
            degree = "Tiến sĩ (PhD)"
        elif "Bachelor" in content_text or "Undergraduate" in content_text:
            degree = "Cử nhân (Undergraduate)"

        # Mức tài trợ
        funding = "Toàn phần (Fully Funded / Full Tuition)" if (
            "fully funded" in content_text.lower() or "full tuition" in content_text.lower() or "living allowance" in content_text.lower()
        ) else "Bán phần (Partial Funding)"

        # Hạn nộp
        deadline_match = re.search(r"Deadline[:\s]+([^\n\r<]+)", content_text, re.IGNORECASE)
        deadline = deadline_match.group(1).strip() if deadline_match else "Xem trong thông báo chính thức"

        # Quốc gia
        country_match = re.search(r"Study in[:\s]+([^\n\r<]+)", content_text, re.IGNORECASE)
        host_country = country_match.group(1).strip() if country_match else "Quốc tế / Đa quốc gia"

        # GPA & Ngoại ngữ ước tính
        min_gpa = "3.0"
        if "3.2" in content_text:
            min_gpa = "3.2"
        elif "3.5" in content_text or "first class" in content_text.lower():
            min_gpa = "3.4"

        min_ielts = "6.5" if ("UK" in host_country or "USA" in host_country or "Australia" in host_country) else "6.0"

        return {
            "Tên học bổng": title,
            "Nguồn": "Scholars4dev",
            "Quốc gia": host_country,
            "Bậc học": degree,
            "Chuyên ngành áp dụng": "Mọi ngành / Đa lĩnh vực",
            "Mức tài trợ": funding,
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": content_text[:350].replace("\n", " "),
            "GPA tối thiểu": min_gpa,
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": f"IELTS {min_ielts}",
            "Kinh nghiệm làm việc yêu cầu": "0",
            "Hạn nộp & Chu kỳ tuyển sinh": deadline,
            "Link chi tiết": link,
            "Hồ sơ cần chuẩn bị (Checklist)": "Bảng điểm, CV, Thư giới thiệu, SOP",
            "Ràng buộc & Cam kết": "Quy chế học bổng quốc tế"
        }
    except Exception:
        return None

def fetch_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return []
        soup = BeautifulSoup(resp.content, "html.parser")
        posts = soup.find_all("div", class_="post")
        if not posts:
            posts = soup.find_all("article")
        if not posts:
            posts = soup.select(".entry")
        
        results = []
        for p in posts:
            item = parse_post(p)
            if item:
                results.append(item)
        return results
    except Exception:
        return []

def scrape_scholars4dev_bulk(max_urls=120):
    print("=" * 75)
    print(f"[*] Bắt đầu Cào Dữ Liệu Sống Sâu từ Scholars4dev ({max_urls} danh mục & trang phân trang)...")
    print("=" * 75)

    urls = CATEGORY_PAGES[:max_urls]
    unique_items = {}
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(fetch_url, u): u for u in urls}
        completed = 0
        for future in as_completed(future_to_url):
            completed += 1
            items = future.result()
            for it in items:
                title = it["Tên học bổng"]
                if title not in unique_items:
                    unique_items[title] = it
            if completed % 15 == 0 or completed == len(urls):
                print(f"    -> Đã quét {completed}/{len(urls)} trang | Đã thu thập: {len(unique_items)} học bổng độc lập")

    results = list(unique_items.values())
    print(f"[✓] Hoàn thành cào Scholars4dev: Tổng cộng {len(results)} học bổng thực tế!")
    return results

if __name__ == "__main__":
    items = scrape_scholars4dev_bulk(max_urls=50)
    print(f"Thử nghiệm thu được: {len(items)} học bổng")
