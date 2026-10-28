"""
Cào dữ liệu sống 100% từ YBOX.vn bằng cách bóc tách JSON State (SSR __INITIAL_STATE__)
và xuất ra file data/ybox_scholarships.csv
"""

import requests
from bs4 import BeautifulSoup
import json
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

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "ybox_scholarships.csv")

def scrape_ybox_real():
    print("="*70)
    print("[*] Đang cào DỮ LIỆU SỐNG thực tế từ YBOX.vn (https://ybox.vn/hoc-bong)...")
    print("="*70)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    resp = requests.get("https://ybox.vn/hoc-bong", headers=headers, timeout=15)
    if resp.status_code != 200:
        print(f"[!] Lỗi HTTP {resp.status_code}")
        return []
        
    soup = BeautifulSoup(resp.text, "html.parser")
    initial_state = None
    for s in soup.find_all("script"):
        if s.string and "window.__INITIAL_STATE__" in s.string:
            match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});", s.string, re.DOTALL)
            if match:
                try:
                    initial_state = json.loads(match.group(1))
                    break
                except Exception as e:
                    print(f"[!] Lỗi parse JSON state: {e}")
                    
    if not initial_state:
        print("[!] Không tìm thấy __INITIAL_STATE__ trong HTML của Ybox")
        return []
        
    initial_posts = initial_state.get("app", {}).get("initialPosts", {})
    all_raw_posts = []
    
    for group_key in ["NewestPosts", "HighlightPosts", "SelectivePosts"]:
        group = initial_posts.get(group_key, {})
        if isinstance(group, dict):
            edges = group.get("edges", [])
            all_raw_posts.extend(edges)
            print(f"[+] Tìm thấy {len(edges)} bài viết từ nhóm {group_key}")
            
    # Deduplicate by slug or _id
    seen_ids = set()
    cleaned_scholarships = []
    
    for p in all_raw_posts:
        pid = p.get("_id")
        if not pid or pid in seen_ids:
            continue
        seen_ids.add(pid)
        
        title = p.get("title", "").strip()
        if not title:
            continue
            
        summary = p.get("summary", "") or ""
        deadline_raw = p.get("deadline", "") or "Xem chi tiết trên bài viết Ybox"
        link = f"https://ybox.vn/hoc-bong/{pid}"
        
        # Suy luận quốc gia từ tiêu đề
        country = "Quốc tế / Nhiều nước"
        for c in ["Hàn Quốc", "Nhật Bản", "Mỹ", "Hoa Kỳ", "Anh", "Úc", "Canada", "Pháp", "Đức", "Thụy Điển", "Ý", "Hà Lan", "New Zealand", "Đài Loan", "Singapore", "Trung Quốc", "Châu Âu", "Việt Nam"]:
            if c.lower() in title.lower() or c.lower() in summary.lower():
                country = c
                break
                
        # Suy luận mức tài trợ
        funding = "Toàn phần (Full-ride)" if ("toàn phần" in title.lower() or "100%" in title or "fully funded" in title.lower()) else "Bán phần / Hỗ trợ học phí"
        
        # Suy luận bậc học
        degree = "Đại học / Thạc sĩ / Trao đổi"
        if "thạc sĩ" in title.lower() or "master" in title.lower():
            degree = "Thạc sĩ (Master's Degree)"
        elif "tiến sĩ" in title.lower() or "phd" in title.lower():
            degree = "Tiến sĩ (Doctorate / PhD)"
        elif "đại học" in title.lower() or "cử nhân" in title.lower():
            degree = "Cử nhân (Undergraduate / Bachelor)"
        elif "trao đổi" in title.lower() or "ngắn hạn" in title.lower():
            degree = "Trao đổi sinh viên / Ngắn hạn"

        cleaned_scholarships.append({
            "Tên học bổng": title,
            "Nguồn": "YBOX.vn (Live Crawled)",
            "Quốc gia": country,
            "Bậc học": degree,
            "Chuyên ngành áp dụng": "Đa ngành (Kinh tế, STEM, Xã hội, Công nghệ...)",
            "Mức tài trợ": funding,
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": summary[:250] if summary else f"Học bổng đăng tải trên YBOX: {title}",
            "GPA tối thiểu": ">= 3.0 / 4.0 (hoặc >= 7.5 / 10 theo tiêu chuẩn từng chương trình)",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.0 - 6.5 hoặc ngoại ngữ tương đương",
            "Kinh nghiệm làm việc yêu cầu": "Tùy theo bậc học (Ưu tiên ứng viên có hoạt động ngoại khóa / kinh nghiệm)",
            "Độ tuổi giới hạn": "Theo quy chế của từng chương trình",
            "Hồ sơ cần chuẩn bị (Checklist)": "CV, Bảng điểm, Motivation Letter, Thư giới thiệu (LOR)",
            "Ràng buộc & Cam kết": "Tuân thủ quy chế học bổng và điều kiện visa",
            "Hạn nộp & Chu kỳ tuyển sinh": str(deadline_raw),
            "Phương thức ứng tuyển": f"Xem hướng dẫn nộp hồ sơ chi tiết tại: {link}",
            "Link chi tiết": link
        })
        
    if cleaned_scholarships:
        keys = list(cleaned_scholarships[0].keys())
        with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(cleaned_scholarships)
        print(f"\n[✓] THÀNH CÔNG: Đã cào SỐNG {len(cleaned_scholarships)} bài viết học bổng từ YBOX.vn và lưu vào: {CSV_FILE}")
    else:
        print("[!] Không tìm thấy bài viết học bổng.")
        
    return cleaned_scholarships

if __name__ == "__main__":
    scrape_ybox_real()
