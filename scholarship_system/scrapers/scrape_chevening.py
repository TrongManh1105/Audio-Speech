import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_FILE = os.path.join(OUTPUT_DIR, "chevening_scholarships.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def scrape_chevening():
    print("="*60)
    print("Crawling: Chevening Official (https://www.chevening.org/scholarships)")
    print("="*60)
    
    scholarships = []
    
    target_pages = [
        {
            "name": "Chevening Scholarship (UK Government Full-Ride Master's)",
            "url": "https://www.chevening.org/scholarships/",
            "type": "Học bổng Chính phủ Toàn phần",
            "desc": "Tài trợ toàn bộ học phí 1 năm Thạc sĩ tại bất kỳ trường ĐH nào ở Vương quốc Anh, vé máy bay khứ hồi, sinh hoạt phí hàng tháng, visa, trợ cấp đến nơi."
        },
        {
            "name": "Chevening Eligibility & Criteria (Điều kiện ứng tuyển)",
            "url": "https://www.chevening.org/scholarships/who-can-apply/eligibility/",
            "type": "Tiêu chuẩn & Điều kiện ứng tuyển",
            "desc": "Quốc tịch Việt Nam/nước đủ điều kiện; Có bằng cử nhân tương đương UK 2:1; Tối thiểu 2 năm kinh nghiệm làm việc (2,800 giờ); Cam kết trở về nước tối thiểu 2 năm sau khi hoàn thành khóa học."
        },
        {
            "name": "Chevening Partner Awards",
            "url": "https://www.chevening.org/scholarships/partner-awards/",
            "type": "Học bổng Đồng tài trợ Đối tác",
            "desc": "Các suất học bổng hợp tác giữa Chevening và các trường đại học hàng đầu Anh Quốc (Oxford, Cambridge, LSE, Imperial...) hoặc các tổ chức doanh nghiệp đối tác."
        },
        {
            "name": "Chevening Fellowships",
            "url": "https://www.chevening.org/fellowships/",
            "type": "Học bổng Nghiên cứu & Chuyên gia",
            "desc": "Các khóa đào tạo chuyên sâu ngắn hạn dành cho các nhà lãnh đạo, chuyên gia, nhà báo, nhà nghiên cứu trong các lĩnh vực an ninh, báo chí, chính sách công."
        }
    ]
    
    for item in target_pages:
        print(f"[*] Đang lấy dữ liệu từ: {item['url']}", flush=True)
        criteria_text = item["desc"]
        deadline_text = "Thường niên: Mở tháng 8, đóng đầu tháng 11 hàng năm"
        try:
            resp = requests.get(item["url"], headers=HEADERS, timeout=4)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.content, "html.parser")
                main_content = soup.find("main") or soup.find("article") or soup.find("body")
                if main_content:
                    page_text = main_content.get_text(separator=" ", strip=True)
                    deadline_search = re.search(r"applications (?:open|close)[^.]*?(?:november|october|august|\d{1,2}\s+[a-z]+\s+\d{4})", page_text, re.IGNORECASE)
                    if deadline_search:
                        deadline_text = deadline_search.group(0).strip()
        except Exception as e:
            print(f"[!] Thông báo (Dùng fallback Chevening): {e}", flush=True)
            
        scholarships.append({
            "Tên học bổng": item["name"],
            "Nguồn": "Chevening (UK Government)",
            "Quốc gia": "Vương quốc Anh (United Kingdom)",
            "Bậc học": "Thạc sĩ (Master's) / Fellowship",
            "Mức tài trợ": "Toàn phần 100% (Học phí + Vé máy bay + Sinh hoạt phí + Visa + Trợ cấp)",
            "Đối tượng áp dụng": "Công dân Việt Nam, đã tốt nghiệp đại học (tương đương UK 2:1), >= 2 năm kinh nghiệm làm việc",
            "Hạn nộp": deadline_text,
            "Tóm tắt điều kiện & Quyền lợi": criteria_text,
            "Link chi tiết": item["url"]
        })
            
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(scholarships[0].keys()))
        writer.writeheader()
        writer.writerows(scholarships)
    print(f"[✓] Đã lưu {len(scholarships)} bản ghi Chevening vào: {CSV_FILE}")
    return scholarships

if __name__ == "__main__":
    scrape_chevening()
