"""
SUPABASE / POSTGRESQL + PGVECTOR SYNC & QUERY ENGINE
Script nạp dữ liệu học bổng từ CSV lên cơ sở dữ liệu PostgreSQL (Supabase/Neon)
và thực thi so khớp hồ sơ ứng viên với xếp hạng đa chỉ số (Hybrid Ranking).
"""

import os
import sys
import csv
import json
import re
from typing import List, Dict, Any

# Đảm bảo in tiếng Việt chuẩn trên Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Kiểm tra thư viện psycopg2
try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    psycopg2 = None

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "all_scholarships_combined.csv")

def parse_min_gpa(gpa_str: str, default: float = 3.0) -> float:
    """Bóc tách và chuẩn hóa GPA về thang 4.0"""
    if not gpa_str:
        return default
    match_4 = re.search(r"(\d+\.\d+)\s*/\s*4\.0", str(gpa_str))
    if match_4:
        return min(float(match_4.group(1)), 4.0)
    match_10 = re.search(r"(\d+\.?\d*)\s*/\s*10", str(gpa_str))
    if match_10:
        val = float(match_10.group(1))
        return round((val / 10.0) * 4.0, 2)
    match_pct = re.search(r"(\d+)%", str(gpa_str))
    if match_pct:
        pct = float(match_pct.group(1))
        return round((pct / 100.0) * 4.0, 2)
    match_gen = re.search(r"(\d+\.?\d*)", str(gpa_str))
    if match_gen:
        v = float(match_gen.group(1))
        if 4.0 < v <= 10.0:
            return round((v / 10.0) * 4.0, 2)
        elif 10.0 < v <= 100.0:
            return round((v / 100.0) * 4.0, 2)
        elif v <= 4.0:
            return v
    return default

def parse_min_ielts(ielts_str: str, default: float = 6.0) -> float:
    """Bóc tách IELTS chuẩn (thang 9.0)"""
    if not ielts_str:
        return default
    match = re.search(r"IELTS[^\d]*(\d+\.?\d*)", str(ielts_str), re.IGNORECASE)
    if match:
        return min(float(match.group(1)), 9.0)
    match_gen = re.search(r"(\d+\.?\d*)", str(ielts_str))
    if match_gen:
        v = float(match_gen.group(1))
        if 4.0 <= v <= 9.0:
            return v
    return default

def parse_work_exp(exp_str: str, default: float = 0.0) -> float:
    """Bóc tách số năm kinh nghiệm"""
    if not exp_str:
        return default
    match = re.search(r"(\d+\.?\d*)\s*năm", str(exp_str), re.IGNORECASE)
    if match:
        return min(float(match.group(1)), 20.0)
    match_hr = re.search(r"(\d+[\d,.]*)\s*giờ", str(exp_str), re.IGNORECASE)
    if match_hr:
        # 2800 giờ tương đương ~2 năm
        return 2.0
    return default


def generate_mock_vector_1536(text: str) -> List[float]:
    """
    Tạo vector đặc trưng 1536 chiều giả lập từ nội dung văn bản.
    (Khi chạy production, thay thế bằng: openai.embeddings.create hoặc bge-m3)
    """
    import hashlib
    # Dùng hashing để vector có tính tất định (Deterministic) với cùng 1 đoạn text
    vector = [0.0] * 1536
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    seed = int(h[:8], 16)
    
    # Tạo giá trị vector chuẩn hóa
    norm_sq = 0.0
    for i in range(1536):
        val = ((seed * (i + 1) * 31) % 1000 - 500) / 500.0
        # Tăng trọng số nếu chứa từ khóa chuyên ngành
        if any(k in text.lower() for k in ["ai", "computer science", "stem", "data"]):
            val += 0.2
        vector[i] = val
        norm_sq += val * val
    
    # Chuẩn hóa L2 norm về độ dài 1.0 (chuẩn Cosine Similarity)
    norm = norm_sq ** 0.5
    return [round(v / norm, 6) for v in vector]

def connect_db(connection_string: str):
    """Tạo kết nối đến PostgreSQL"""
    if not psycopg2:
        raise ImportError("Vui lòng cài đặt psycopg2: pip install psycopg2-binary")
    return psycopg2.connect(connection_string)

def upload_scholarships_to_supabase(connection_string: str, limit: int = 50):
    """Đọc dữ liệu CSV cào về và đẩy lên PostgreSQL (Supabase)"""
    print(f"\n[+] Đang kết nối đến PostgreSQL...")
    conn = connect_db(connection_string)
    cur = conn.cursor()

    if not os.path.exists(CSV_PATH):
        print(f"[-] Không tìm thấy file dữ liệu: {CSV_PATH}")
        return

    print(f"[+] Đang đọc dữ liệu từ: {CSV_PATH}")
    rows_to_insert = []
    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if idx >= limit:
                break
            title = row.get("Tên học bổng", "")
            source = row.get("Nguồn", "")
            country = row.get("Quốc gia", "")
            degree = row.get("Bậc học", "")
            major = row.get("Chuyên ngành áp dụng", "")
            funding = row.get("Mức tài trợ", "")
            funding_detail = row.get("Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)", "")
            min_gpa = parse_min_gpa(row.get("GPA tối thiểu", ""), 3.0)
            min_ielts = parse_min_ielts(row.get("Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)", ""), 6.0)
            work_exp = parse_work_exp(row.get("Kinh nghiệm làm việc yêu cầu", ""), 0.0)
            link = row.get("Link chi tiết", "")



            # Tạo đoạn ngữ cảnh văn bản để embed
            embed_text = f"Title: {title}. Country: {country}. Degree: {degree}. Major: {major}. Benefits: {funding_detail}."
            vector_1536 = generate_mock_vector_1536(embed_text)

            rows_to_insert.append((
                title, source, country, degree, major, funding, funding_detail,
                min_gpa, min_ielts, work_exp, link, embed_text, json.dumps(vector_1536)
            ))

    print(f"[+] Đang nạp {len(rows_to_insert)} học bổng vào cơ sở dữ liệu Supabase...")
    insert_query = """
    INSERT INTO scholarships (
        title, source_name, host_country, degree_level, major_applied,
        funding_type, funding_details, min_gpa, min_ielts, min_work_exp_years,
        link, raw_content, embedding
    )
    VALUES %s;
    """
    execute_values(cur, insert_query, rows_to_insert, template="(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)")
    conn.commit()
    print(f"[✓] ĐÃ NẠP THÀNH CÔNG {len(rows_to_insert)} HỌC BỔNG VÀO SUPABASE!")
    cur.close()
    conn.close()

DEFAULT_SUPABASE_URL = "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

if __name__ == "__main__":
    print("=" * 80)
    print("SCRIPT NẠP VÀ KẾT NỐI POSTGRESQL / SUPABASE (PGVECTOR)")
    print("=" * 80)
    
    db_url = os.environ.get("DATABASE_URL", DEFAULT_SUPABASE_URL)
    print(f"[+] Sử dụng Database: Supabase Project (wzsztxegmqeuwgozlggt)")
    upload_scholarships_to_supabase(db_url, limit=50)

