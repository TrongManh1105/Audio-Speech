import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import psycopg2

SUPABASE_URL = "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

def init_database():
    print("[+] Đang kết nối tới Supabase PostgreSQL...")
    conn = psycopg2.connect(SUPABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()

    print("[+] Đang đọc file schema_pgvector.sql...")
    with open("schema_pgvector.sql", "r", encoding="utf-8") as f:
        sql = f.read()

    print("[+] Đang khởi tạo extension pgvector, các bảng và index HNSW...")
    cur.execute(sql)
    print("[✓] THỰC THI SCHEMA THÀNH CÔNG!")

    cur.execute("SELECT tablename FROM pg_tables WHERE schemaname='public';")
    tables = cur.fetchall()
    print("[✓] Các bảng đã tạo trên Supabase:", tables)

    cur.close()
    conn.close()

if __name__ == "__main__":
    init_database()
