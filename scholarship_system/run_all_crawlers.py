import os
import sys

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import csv

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

from scrapers.scrape_scholars4dev import scrape_scholars4dev
from scrapers.scrape_youthop import scrape_youthop
from scrapers.scrape_chevening import scrape_chevening
from scrapers.scrape_ybox import scrape_ybox
from scrapers.scrape_studyinkorea import scrape_studyinkorea

def run_all():
    output_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("BẮT ĐẦU CÀO DỮ LIỆU HỌC BỔNG TỪ 5 NGUỒN")
    print("="*70 + "\n")
    
    all_data = []
    
    # 1. Scholars4dev
    try:
        s4d = scrape_scholars4dev(max_pages=2)
        all_data.extend(s4d)
    except Exception as e:
        print(f"[!] Lỗi Scholars4dev: {e}")
        
    # 2. Youth Opportunities
    try:
        yo = scrape_youthop(max_pages=2)
        all_data.extend(yo)
    except Exception as e:
        print(f"[!] Lỗi Youth Opportunities: {e}")
        
    # 3. Chevening
    try:
        chev = scrape_chevening()
        all_data.extend(chev)
    except Exception as e:
        print(f"[!] Lỗi Chevening: {e}")
        
    # 4. YBOX
    try:
        yb = scrape_ybox(max_pages=2)
        all_data.extend(yb)
    except Exception as e:
        print(f"[!] Lỗi YBOX: {e}")
        
    # 5. Study in Korea
    try:
        sik = scrape_studyinkorea()
        all_data.extend(sik)
    except Exception as e:
        print(f"[!] Lỗi Study in Korea: {e}")
        
    # Xuất file tổng hợp
    combined_file = os.path.join(output_dir, "all_scholarships_combined.csv")
    if all_data:
        with open(combined_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_data[0].keys()))
            writer.writeheader()
            writer.writerows(all_data)
        print("\n" + "="*70)
        print(f"[HOÀN THÀNH] Đã xuất thành công 5 file CSV riêng và 1 file tổng hợp ({len(all_data)} học bổng)")
        print(f"Thư mục chứa dữ liệu: {output_dir}")
        print("="*70)
    else:
        print("[!] Không có dữ liệu tổng hợp.")

if __name__ == "__main__":
    run_all()
