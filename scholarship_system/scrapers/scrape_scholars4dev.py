import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import re
import time

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_FILE = os.path.join(OUTPUT_DIR, "scholars4dev_scholarships.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
}

def extract_field_info(soup_or_text, label):
    pattern = rf"{label}[:\s]+(.*?)(?=\n[A-Z][a-z]+[:\s]|$)"
    match = re.search(pattern, soup_or_text, re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return ""

def scrape_scholars4dev(max_pages=3):
    print("="*60)
    print("Crawling: Scholars4dev (https://www.scholars4dev.com)")
    print("="*60)
    
    base_url = "https://www.scholars4dev.com/category/scholarships-list/"
    scholarships = []
    
    for page in range(1, max_pages + 1):
        url = base_url if page == 1 else f"{base_url}page/{page}/"
        print(f"[*] Đang tải trang {page}: {url}")
        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            if resp.status_code != 200:
                print(f"[!] Lỗi HTTP {resp.status_code} khi tải {url}")
                break
            
            soup = BeautifulSoup(resp.content, "html.parser")
            posts = soup.find_all("div", class_="post")
            if not posts:
                posts = soup.find_all("article")
            if not posts:
                posts = soup.select(".entry")
                
            print(f"    Tìm thấy {len(posts)} bài viết trên trang {page}")
            
            for post in posts:
                title_elem = post.find(["h2", "h1", "h3"])
                if not title_elem:
                    continue
                a_tag = title_elem.find("a")
                if not a_tag:
                    continue
                
                title = a_tag.get_text(strip=True)
                link = a_tag.get("href", "")
                
                content_elem = post.find("div", class_="entry clearfix") or post.find("div", class_="post_content") or post
                content_text = content_elem.get_text(separator="\n", strip=True) if content_elem else ""
                
                # Extract meta attributes from content snippet
                degree = "Bachelors / Masters / PhD"
                if "Master" in content_text or "Masters" in content_text:
                    degree = "Master"
                elif "PhD" in content_text or "Doctoral" in content_text:
                    degree = "PhD / Doctoral"
                elif "Bachelor" in content_text or "Undergraduate" in content_text:
                    degree = "Bachelor"
                    
                funding = "Toàn phần / Bán phần"
                if "Fully Funded" in content_text or "full tuition" in content_text.lower() or "living allowance" in content_text.lower():
                    funding = "Toàn phần (Fully Funded / Full Tuition)"
                elif "partial" in content_text.lower():
                    funding = "Bán phần (Partial Funding)"
                    
                # Deadline search
                deadline_match = re.search(r"Deadline[:\s]+([^\n\r<]+)", content_text, re.IGNORECASE)
                deadline = deadline_match.group(1).strip() if deadline_match else "Xem trong bài viết"
                
                # Host country
                country_match = re.search(r"Study in[:\s]+([^\n\r<]+)", content_text, re.IGNORECASE)
                host_country = country_match.group(1).strip() if country_match else "Quốc tế / Nhiều nước"
                
                # Target group
                target_match = re.search(r"Target group[:\s]+([^\n\r<]+)", content_text, re.IGNORECASE)
                target_group = target_match.group(1).strip() if target_match else "Sinh viên quốc tế (gồm Việt Nam)"
                
                scholarships.append({
                    "Tên học bổng": title,
                    "Nguồn": "Scholars4dev",
                    "Quốc gia": host_country,
                    "Bậc học": degree,
                    "Mức tài trợ": funding,
                    "Đối tượng áp dụng": target_group,
                    "Hạn nộp": deadline,
                    "Tóm tắt điều kiện & Quyền lợi": content_text[:350].replace("\n", " "),
                    "Link chi tiết": link
                })
            
            time.sleep(1)
        except Exception as e:
            print(f"[!] Lỗi khi cào Scholars4dev: {e}")
            break
            
    if scholarships:
        with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(scholarships[0].keys()))
            writer.writeheader()
            writer.writerows(scholarships)
        print(f"[✓] Đã lưu {len(scholarships)} học bổng vào: {CSV_FILE}")
    else:
        print("[!] Không tìm thấy dữ liệu học bổng từ Scholars4dev.")
    return scholarships

if __name__ == "__main__":
    scrape_scholars4dev(max_pages=2)
