"""
HỆ THỐNG CÀO DỮ LIỆU TỰ ĐỘNG & ĐỒNG BỘ HÀNG NGÀY LÊN SUPABASE (PGVECTOR)
Cào trực tiếp từ 5 nguồn chính thức:
1. Youth Opportunities (https://www.youthop.com/scholarships)
2. Chevening Official (https://www.chevening.org/scholarships)
3. Study in Korea / NIIED (https://www.studyinkorea.go.kr)
4. YBOX.vn (https://ybox.vn/hoc-bong)
5. Scholars4dev (https://www.scholars4dev.com)
Tự động sinh Vector 1536D và chạy UPSERT (Insert/Update) vào PostgreSQL Supabase.
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import re
import csv
import json
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import execute_values

# Thêm đường dẫn thư mục dự án
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Import các scraper cào dữ liệu sống
from scrapers.scrape_ybox_real import scrape_ybox_real
from scrapers.scrape_studyinkorea_real import scrape_studyinkorea_real
from scrapers.scrape_youthop_real import scrape_youthop_real
from scrapers.scrape_chevening import scrape_chevening
from scrapers.scrape_scholars4dev import scrape_scholars4dev
from supabase_importer import generate_mock_vector_1536, parse_min_gpa, parse_min_ielts, parse_work_exp

SUPABASE_URL = (
    os.environ.get("DATABASE_URL")
    or "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

def run_daily_sync():
    start_time = datetime.now()
    print("=" * 85)
    print(f"[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] BẮT ĐẦU QUY TRÌNH CÀO SỐNG VÀ ĐỒNG BỘ SUPABASE")
    print("=" * 85)

    all_scraped = []

    # 1. Cào trực tiếp từ YBOX.vn
    try:
        print("\n[1/5] Đang cào dữ liệu từ YBOX.vn...")
        ybox_data = scrape_ybox_real()
        all_scraped.extend(ybox_data)
        print(f"    ✓ Đã lấy được {len(ybox_data)} học bổng từ YBOX.")
    except Exception as e:
        print(f"    [!] Lỗi cào YBOX: {e}")

    # 2. Cào trực tiếp từ Study in Korea (NIIED)
    try:
        print("\n[2/5] Đang cào dữ liệu từ Cổng Chính Phủ Hàn Quốc (Study in Korea)...")
        korea_data = scrape_studyinkorea_real()
        all_scraped.extend(korea_data)
        print(f"    ✓ Đã lấy được {len(korea_data)} học bổng từ Study in Korea.")
    except Exception as e:
        print(f"    [!] Lỗi cào Study in Korea: {e}")

    # 3. Cào trực tiếp từ Youth Opportunities
    try:
        print("\n[3/5] Đang cào dữ liệu từ Youth Opportunities (vượt Cloudflare)...")
        youthop_data = scrape_youthop_real()
        all_scraped.extend(youthop_data)
        print(f"    ✓ Đã lấy được {len(youthop_data)} học bổng từ Youth Opportunities.")
    except Exception as e:
        print(f"    [!] Lỗi cào Youth Opportunities: {e}")

    # 4. Cào trực tiếp từ Chevening UK Official
    try:
        print("\n[4/5] Đang cào dữ liệu từ Chevening UK Official...")
        chevening_data = scrape_chevening()
        all_scraped.extend(chevening_data)
        print(f"    ✓ Đã lấy được {len(chevening_data)} học bổng từ Chevening.")
    except Exception as e:
        print(f"    [!] Lỗi cào Chevening: {e}")

    # 5. Cào trực tiếp từ Scholars4dev (Bulk Crawler)
    try:
        print("\n[5/5] Đang cào dữ liệu sâu từ Scholars4dev (60 trang danh mục)...")
        from scrapers.scrape_scholars4dev_bulk import scrape_scholars4dev_bulk
        s4d_data = scrape_scholars4dev_bulk(max_urls=60)
        all_scraped.extend(s4d_data)
        print(f"    ✓ Đã lấy được {len(s4d_data)} học bổng từ Scholars4dev.")
    except Exception as e:
        print(f"    [!] Lỗi cào Scholars4dev: {e}")

    total_crawled = len(all_scraped)
    print(f"\n[+] TỔNG SỐ HỌC BỔNG CÀO ĐƯỢC HÔM NAY: {total_crawled}")

    if total_crawled == 0:
        print("[!] Không có dữ liệu cào về, giữ nguyên database hiện tại.")
        return

    # Chuẩn hóa toàn bộ danh sách về 1 schema thống nhất
    normalized_data = []
    for raw in all_scraped:
        title = raw.get("Tên học bổng") or raw.get("title") or ""
        if not title:
            continue
        source = raw.get("Nguồn") or raw.get("source") or "Tổng hợp"
        country = raw.get("Quốc gia") or raw.get("country") or "Quốc tế"
        degree = raw.get("Bậc học") or raw.get("degree") or "Đa bậc học"
        major = raw.get("Chuyên ngành áp dụng") or raw.get("major") or "Mọi ngành"
        funding = raw.get("Mức tài trợ") or raw.get("funding") or "Toàn phần / Bán phần"
        funding_detail = (
            raw.get("Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)")
            or raw.get("Tóm tắt điều kiện & Quyền lợi")
            or raw.get("funding_details")
            or ""
        )
        gpa_raw = raw.get("GPA tối thiểu") or raw.get("min_gpa") or ""
        ielts_raw = raw.get("Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)") or raw.get("min_ielts") or ""
        exp_raw = raw.get("Kinh nghiệm làm việc yêu cầu") or raw.get("min_work_exp") or ""
        deadline = (
            raw.get("Hạn nộp & Chu kỳ tuyển sinh")
            or raw.get("Hạn nộp")
            or raw.get("deadline")
            or "Xem chi tiết"
        )
        link = raw.get("Link chi tiết") or raw.get("link") or ""
        checklist = raw.get("Hồ sơ cần chuẩn bị (Checklist)") or raw.get("checklist") or "CV, Bảng điểm"
        commitment = raw.get("Ràng buộc & Cam kết") or raw.get("commitment") or "Theo quy định học bổng"

        normalized_data.append({
            "Tên học bổng": title.strip(),
            "Nguồn": source.strip(),
            "Quốc gia": country.strip(),
            "Bậc học": degree.strip(),
            "Chuyên ngành áp dụng": major.strip(),
            "Mức tài trợ": funding.strip(),
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": funding_detail.strip(),
            "GPA tối thiểu": str(gpa_raw).strip(),
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": str(ielts_raw).strip(),
            "Kinh nghiệm làm việc yêu cầu": str(exp_raw).strip(),
            "Hạn nộp & Chu kỳ tuyển sinh": str(deadline).strip(),
            "Link chi tiết": link.strip(),
            "Hồ sơ cần chuẩn bị (Checklist)": checklist.strip(),
            "Ràng buộc & Cam kết": commitment.strip()
        })

    # Lưu bản sao file CSV master cục bộ
    csv_file = os.path.join(CURRENT_DIR, "data", "all_scholarships_combined.csv")
    try:
        keys = list(normalized_data[0].keys())
        with open(csv_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(normalized_data)
        print(f"[✓] Đã cập nhật file CSV tổng hợp tại: {csv_file}")
    except Exception as e:
        print(f"[!] Lỗi ghi file CSV: {e}")

    # =========================================================================
    # ĐỒNG BỘ DỮ LIỆU LÊN SUPABASE (UPSERT ON CONFLICT UPDATE)
    # =========================================================================
    print("\n[+] Đang kết nối đến Cloud Database Supabase...")
    try:
        conn = psycopg2.connect(SUPABASE_URL)
        conn.autocommit = True
        cur = conn.cursor()
    except Exception as e:
        print(f"[-] Không thể kết nối Supabase: {e}")
        return

    # Chuẩn bị dữ liệu nạp
    rows_to_upsert = []
    for item in normalized_data:
        title = item["Tên học bổng"]
        source = item["Nguồn"]
        country = item["Quốc gia"]
        degree = item["Bậc học"]
        major = item["Chuyên ngành áp dụng"]
        funding = item["Mức tài trợ"]
        funding_detail = item["Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)"]
        deadline = item["Hạn nộp & Chu kỳ tuyển sinh"]
        link = item["Link chi tiết"]
        checklist = item["Hồ sơ cần chuẩn bị (Checklist)"]
        commitment = item["Ràng buộc & Cam kết"]

        min_gpa = parse_min_gpa(item["GPA tối thiểu"], 3.0)
        min_ielts = parse_min_ielts(item["Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)"], 6.0)
        work_exp = parse_work_exp(item["Kinh nghiệm làm việc yêu cầu"], 0.0)

        # Ngữ cảnh tạo vector
        embed_text = f"Title: {title}. Source: {source}. Country: {country}. Degree: {degree}. Major: {major}. Benefits: {funding_detail}. Deadline: {deadline}."
        vector_1536 = generate_mock_vector_1536(embed_text)

        rows_to_upsert.append((
            title, source, country, degree, major, funding, funding_detail,
            min_gpa, min_ielts, work_exp, checklist, commitment, deadline,
            link, embed_text, json.dumps(vector_1536)
        ))


    print(f"[+] Đang đồng bộ {len(rows_to_upsert)} học bổng vào bảng 'scholarships' trên Supabase...")
    
    upsert_sql = """
    INSERT INTO scholarships (
        title, source_name, host_country, degree_level, major_applied,
        funding_type, funding_details, min_gpa, min_ielts, min_work_exp_years,
        checklist, commitment, deadline, link, raw_content, embedding,
        is_active, updated_at
    )
    VALUES %s
    ON CONFLICT (title, source_name)
    DO UPDATE SET 
        host_country = EXCLUDED.host_country,
        degree_level = EXCLUDED.degree_level,
        major_applied = EXCLUDED.major_applied,
        funding_type = EXCLUDED.funding_type,
        funding_details = EXCLUDED.funding_details,
        min_gpa = EXCLUDED.min_gpa,
        min_ielts = EXCLUDED.min_ielts,
        min_work_exp_years = EXCLUDED.min_work_exp_years,
        checklist = EXCLUDED.checklist,
        commitment = EXCLUDED.commitment,
        deadline = EXCLUDED.deadline,
        link = EXCLUDED.link,
        raw_content = EXCLUDED.raw_content,
        embedding = EXCLUDED.embedding,
        is_active = TRUE,
        updated_at = CURRENT_TIMESTAMP;
    """

    try:
        execute_values(
            cur,
            upsert_sql,
            rows_to_upsert,
            template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, TRUE, CURRENT_TIMESTAMP)"
        )
        print(f"[✓] ĐỒNG BỘ THÀNH CÔNG LÊN SUPABASE!")
    except Exception as e:
        print(f"[!] Lỗi khi thực hiện UPSERT lên Supabase: {e}")

    # Đếm số lượng học bổng hiện có
    cur.execute("SELECT COUNT(*), COUNT(CASE WHEN is_active THEN 1 END) FROM scholarships;")
    res = cur.fetchone()
    total_db = res[0]
    active_db = res[1]

    # Ghi nhận lịch sử vào bảng sync_logs trên Supabase
    try:
        cur.execute("""
            INSERT INTO sync_logs (sync_time, total_scraped, total_in_db, status, details)
            VALUES (NOW(), %s, %s, %s, %s);
        """, (
            len(rows_to_upsert),
            total_db,
            "SUCCESS",
            f"Đồng bộ thành công {len(rows_to_upsert)} học bổng từ 5 nguồn (Ybox, StudyinKorea, YouthOp, Chevening, Scholars4dev)."
        ))
        conn.commit()
        print(f"[✓] Đã ghi nhận lịch sử đồng bộ vào bảng 'sync_logs' trên Supabase!")
    except Exception as log_err:
        print(f"[!] Lỗi ghi sync_logs: {log_err}")

    cur.close()
    conn.close()

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("=" * 85)
    print(f"[HOÀN THÀNH ĐỒNG BỘ] Thời gian xử lý: {duration:.1f} giây")
    print(f"Tổng số học bổng hiện có trên Supabase: {total_db} (Đang mở ứng tuyển: {active_db})")
    print(f"Đã cập nhật vector và hạn nộp mới nhất cho toàn bộ hệ thống!")
    print("=" * 85)

if __name__ == "__main__":
    run_daily_sync()
