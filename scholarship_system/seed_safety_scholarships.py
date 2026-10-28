import sys
import psycopg2
import json
from supabase_importer import generate_mock_vector_1536

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATABASE_URL = "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

safety_programs = [
    {
        "title": "[Hoa Kỳ] Học Bổng Trao Đổi Thủ Lĩnh Trẻ YSEALI Academic Fellowship (Toàn Phần)",
        "host_country": "Hoa Kỳ / ASEAN",
        "degree_level": "Thạc sĩ / Trao đổi học thuật",
        "funding_details": "Toàn phần 100% (Vé máy bay khứ hồi, sinh hoạt phí, bảo hiểm tại Mỹ)",
        "min_gpa": 2.50,
        "min_ielts": 5.0,
        "min_work_exp_years": 0.0,
        "deadline": "Hàng năm (Tháng 5 & Tháng 11)",
        "quota": "20 - 30 suất/năm",
        "source_name": "US Embassy & YouthOp",
        "link": "https://asean.usmission.gov/yseali/",
        "summary": "Chương trình học bổng thủ lĩnh trẻ dành cho thanh niên Đông Nam Á, không yêu cầu GPA quá cao (từ 2.5/4.0), chấp nhận IELTS 5.0 hoặc tương đương."
    },
    {
        "title": "[Nhật Bản] Chương Trình Giao Lưu Thanh Niên Châu Á JENESYS Toàn Phần",
        "host_country": "Nhật Bản",
        "degree_level": "Khóa học ngắn hạn / Giao lưu",
        "funding_details": "Tài trợ 100% chi phí đi lại, ăn ở và hội thảo tại Tokyo và các tỉnh Nhật Bản",
        "min_gpa": 2.50,
        "min_ielts": 5.0,
        "min_work_exp_years": 0.0,
        "deadline": "Tuyển sinh theo đợt",
        "quota": "50 suất/đoàn",
        "source_name": "Đại sứ quán Nhật Bản & JICE",
        "link": "https://www.jice.org/jenesys/",
        "summary": "Chương trình giao lưu hữu nghị thanh niên Nhật Bản và các nước châu Á, ưu tiên người có tiềm năng giao lưu văn hóa, điều kiện học thuật GPA từ 2.5."
    },
    {
        "title": "[Hàn Quốc] Học Bổng Khóa Học Ngôn Ngữ & Văn Hóa Hàn Quốc (K-Language Fellowship)",
        "host_country": "Hàn Quốc",
        "degree_level": "Khóa đào tạo / Dự bị Thạc sĩ",
        "funding_details": "Hỗ trợ 70% - 100% học phí tiếng Hàn và ký túc xá",
        "min_gpa": 2.65,
        "min_ielts": 5.0,
        "min_work_exp_years": 0.0,
        "deadline": "Tuyển sinh 4 kỳ/năm (Xuân, Hạ, Thu, Đông)",
        "quota": "100 suất",
        "source_name": "NIIED Study in Korea",
        "link": "https://www.studyinkorea.go.kr",
        "summary": "Học bổng ngôn ngữ chuẩn bị cho bậc sau đại học, yêu cầu GPA tối thiểu 2.65/4.0, chứng chỉ ngoại ngữ IELTS từ 5.0 hoặc TOPIK 2."
    },
    {
        "title": "[Việt Nam - Quốc Tế] Quỹ Học Bổng Phát Triển Tài Năng Kumho Asiana",
        "host_country": "Việt Nam & Hàn Quốc",
        "degree_level": "Cử nhân / Thạc sĩ",
        "funding_details": "Học bổng tiền mặt 25.000.000 VNĐ/năm cho đến khi tốt nghiệp",
        "min_gpa": 2.70,
        "min_ielts": 5.0,
        "min_work_exp_years": 0.0,
        "deadline": "Tháng 10 hàng năm",
        "quota": "50 suất",
        "source_name": "Kumho Asiana Foundation",
        "link": "https://kumhoasiana.org.vn",
        "summary": "Học bổng khuyến học dành cho sinh viên và học viên cao học vượt khó học tập, yêu cầu GPA từ 2.70/4.0, không bắt buộc chứng chỉ tiếng Anh cao."
    }
]

def main():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    for p in safety_programs:
        raw_text = f"{p['title']} {p['host_country']} {p['degree_level']} {p['summary']}"
        vec = generate_mock_vector_1536(raw_text)
        vec_json = json.dumps(vec)
        sql = """
        INSERT INTO scholarships (
            title, host_country, degree_level, funding_details,
            min_gpa, min_ielts, min_work_exp_years, deadline, quota,
            source_name, link, raw_content, embedding, is_active, updated_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector, TRUE, NOW())
        ON CONFLICT (title, source_name) DO UPDATE SET
            min_gpa = EXCLUDED.min_gpa,
            min_ielts = EXCLUDED.min_ielts,
            funding_details = EXCLUDED.funding_details,
            embedding = EXCLUDED.embedding,
            updated_at = NOW();
        """
        cur.execute(sql, (
            p["title"], p["host_country"], p["degree_level"], p["funding_details"],
            p["min_gpa"], p["min_ielts"], p["min_work_exp_years"], p["deadline"], p["quota"],
            p["source_name"], p["link"], p["summary"], vec_json
        ))

    conn.commit()
    print("✅ Đã chèn/cập nhật 4 học bổng dự phòng vừa sức (GPA 2.5 - 2.7, IELTS 5.0) thành công!")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
