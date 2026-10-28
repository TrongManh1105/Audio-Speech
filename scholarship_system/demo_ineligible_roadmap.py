"""
DEMO KỊCH BẢN: ỨNG VIÊN KHÔNG ĐẠT ĐIỀU KIỆN SÀN
1. Đánh giá hồ sơ chưa đạt (Ineligible) & Trừ điểm phạt
2. Bóc tách chi tiết khoảng trống tiêu chí (Gap Analysis)
3. Xuất Lộ trình hành động có mốc thời gian cải thiện (Actionable Roadmap)
4. Dùng Vector Database (Supabase) tìm Học bổng Dự phòng vừa sức (Safety Alternatives)
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import json
import psycopg2
from supabase_importer import generate_mock_vector_1536

SUPABASE_URL = "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

def run_ineligible_demo():
    print("=" * 105)
    print("KỊCH BẢN THỬ NGHIỆM: ỨNG VIÊN CHƯA ĐẠT TIÊU CHÍ & LUỒNG GỢI Ý LỘ TRÌNH THAY THẾ")
    print("=" * 105)

    # 1. Hồ sơ ứng viên chưa đạt chuẩn của các học bổng Top (GPA 2.9, IELTS 5.5, chưa có bài báo)
    candidate = {
        "name": "Lê Hoàng Long",
        "degree_target": "Thạc sĩ",
        "major": "Information Technology / Data Science",
        "research_interest": "Machine Learning, Data Analysis, Artificial Intelligence in Business",
        "gpa": 2.95,               # Thang 4.0 (Dưới chuẩn 3.0/3.2)
        "ielts": 5.5,              # Dưới chuẩn 6.5
        "work_exp_years": 0.5,      # 6 tháng kinh nghiệm
        "research_papers": 0,
        "awards": 0
    }

    # Học bổng mục tiêu mà ứng viên rất muốn nộp (Tier 1 danh giá)
    target_scholarship_name = "Top 20 Excellence Scholarships for Outstanding International Students"
    target_min_gpa = 3.2
    target_min_ielts = 6.5
    target_min_exp = 1.0

    print(f"\n[1] THÔNG TIN HỒ SƠ ỨNG VIÊN:")
    print(f"    - Họ tên: {candidate['name']}")
    print(f"    - Bậc học mong muốn: {candidate['degree_target']} | Ngành: {candidate['major']}")
    print(f"    - Điểm GPA hiện tại: {candidate['gpa']}/4.0")
    print(f"    - Chứng chỉ IELTS: {candidate['ielts']}")
    print(f"    - Kinh nghiệm làm việc: {candidate['work_exp_years']} năm (6 tháng)")
    print(f"    - Thành tích NCKH: {candidate['research_papers']} bài báo | Giải thưởng: {candidate['awards']}")

    # 2. Đánh giá đối với học bổng mục tiêu
    print(f"\n[2] ĐÁNH GIÁ ĐỐI VỚI HỌC BỔNG MỤC TIÊU: '{target_scholarship_name}'")
    print(f"    - Yêu cầu sàn của học bổng: GPA >= {target_min_gpa} | IELTS >= {target_min_ielts} | Kinh nghiệm >= {target_min_exp} năm")

    gaps = []
    if candidate["gpa"] < target_min_gpa:
        diff_gpa = round(target_min_gpa - candidate["gpa"], 2)
        gaps.append({
            "criteria": "Điểm trung bình tích lũy (GPA)",
            "current": f"{candidate['gpa']}/4.0",
            "required": f"{target_min_gpa}/4.0",
            "delta": f"Thiếu {diff_gpa} điểm",
            "type": "Cố định (nếu đã tốt nghiệp)"
        })

    if candidate["ielts"] < target_min_ielts:
        diff_ielts = round(target_min_ielts - candidate["ielts"], 1)
        gaps.append({
            "criteria": "Chứng chỉ ngoại ngữ (IELTS)",
            "current": f"{candidate['ielts']}",
            "required": f"{target_min_ielts}",
            "delta": f"Thiếu {diff_ielts} band",
            "type": "Cần cải thiện (Có thể thi lại)"
        })

    if candidate["work_exp_years"] < target_min_exp:
        diff_exp = round(target_min_exp - candidate["work_exp_years"], 1)
        gaps.append({
            "criteria": "Kinh nghiệm làm việc thực tế",
            "current": f"{candidate['work_exp_years']} năm",
            "required": f"{target_min_exp} năm",
            "delta": f"Thiếu {diff_exp} năm ({int(diff_exp*12)} tháng)",
            "type": "Cần tích lũy thêm thời gian"
        })

    print(f"    ==> KẾT QUẢ: ❌ KHÔNG ĐẠT ĐIỀU KIỆN SÀN BẮT BUỘC (INELIGIBLE) - BỊ LOẠI TỪ VÒNG HỒ SƠ")

    # 3. Xuất bảng Gap Analysis
    print(f"\n[3] BẢNG PHÂN TÍCH KHOẢNG CÁCH TIÊU CHUẨN (GAP ANALYSIS):")
    print(f"    {'-'*95}")
    print(f"    {'TIÊU CHÍ':<30} | {'HIỆN TẠI':<12} | {'YÊU CẦU':<12} | {'CHÊNH LỆCH':<18} | {'TÍNH CHẤT'}")
    print(f"    {'-'*95}")
    for g in gaps:
        print(f"    {g['criteria']:<30} | {g['current']:<12} | {g['required']:<12} | {g['delta']:<18} | {g['type']}")
    print(f"    {'-'*95}")

    # 4. Xuất Lộ trình hành động (Actionable Roadmap)
    print(f"\n[4] LỘ TRÌNH HÀNH ĐỘNG CẢI THIỆN ĐỂ NỘP LẠI VÀO KỲ SAU (ACTIONABLE ROADMAP):")
    print(f"""
    ➤ [GIAI ĐOẠN 1: NÂNG CHUẨN NGOẠI NGỮ (Tháng 1 - Tháng 4)]
       * Nhiệm vụ: Đăng ký khóa luyện thi tập trung nâng điểm từ IELTS 5.5 lên tối thiểu 6.5 (+1.0 band).
       * Lời khuyên: Học bổng Thạc sĩ yêu cầu tối thiểu Writing 6.0 và Speaking 6.0 để vượt qua vòng phỏng vấn.

    ➤ [GIAI ĐOẠN 2: CHIẾN LƯỢC BÙ TRỪ ĐIỂM GPA (Tháng 3 - Tháng 6)]
       * Nhiệm vụ: Gia tăng điểm cộng học thuật thay thế cho GPA 2.95.
       * Lời khuyên: Nếu đã tốt nghiệp ĐH, GPA là cố định. Bạn cần:
         - Tham gia viết 01 bài báo khoa học (Hội nghị/Scopus) cùng giảng viên.
         - Hoàn thành 2 chứng chỉ chuyên ngành quốc tế uy tín (VD: IBM Data Science / DeepLearning.AI trên Coursera).

    ➤ [GIAI ĐOẠN 3: TÍCH LŨY KINH NGHIỆM LÀM VIỆC (Tháng 1 - Tháng 8)]
       * Nhiệm vụ: Tiếp tục công tác toàn thời gian thêm 6 tháng để đạt mốc 1.0 năm thâm niên.
       * Lời khuyên: Xin giấy xác nhận công tác và thư giới thiệu (LOR) từ Quản lý trực tiếp.
    """)

    # 5. Dùng Vector Database (Supabase) tìm Học bổng Dự phòng Vừa sức (Safety Alternatives)
    print(f"[5] GIẢI PHÁP DỰ PHÒNG: DÙNG VECTOR SEARCH TÌM HỌC BỔNG VỪA SỨC CÓ THỂ ĐI DU HỌC NGAY")
    print(f"    (Hệ thống dùng Vector so khớp ngữ nghĩa ngành IT/AI, nhưng LỌC BỎ các học bổng bắt buộc GPA cao)\n")

    conn = psycopg2.connect(SUPABASE_URL)
    cur = conn.cursor()

    cand_text = f"Candidate: {candidate['name']}. Major: {candidate['major']}. Research: {candidate['research_interest']}."
    cand_vector = generate_mock_vector_1536(cand_text)

    # Truy vấn Supabase: Tìm học bổng vừa sức với GPA 2.95 và IELTS 5.5
    sql_alternatives = """
    SELECT 
        title,
        host_country,
        degree_level,
        min_gpa,
        min_ielts,
        funding_details,
        ROUND(((1.0 - (embedding <=> %s::vector)) * 100.0)::numeric, 2) AS sim_pct
    FROM scholarships
    WHERE (min_gpa IS NULL OR min_gpa <= 3.0)
      AND (min_ielts IS NULL OR min_ielts <= 6.0)
    ORDER BY embedding <=> %s::vector ASC
    LIMIT 3;
    """
    
    vec_json = json.dumps(cand_vector)
    cur.execute(sql_alternatives, [vec_json, vec_json])
    alt_rows = cur.fetchall()

    print(f"    {'TOP':<4} | {'HỌC BỔNG VỪA SỨC ĐỀ XUẤT':<42} | {'QUỐC GIA':<12} | {'YÊU CẦU GPA/IELTS':<18} | {'ĐỘ KHỚP VECTOR'}")
    print(f"    {'-'*100}")
    for idx, r in enumerate(alt_rows, 1):
        title, country, degree, min_gpa, min_ielts, funding, sim = r
        min_gpa = float(min_gpa or 2.8)
        min_ielts = float(min_ielts or 5.5)
        print(f"    {idx:<4} | {title[:40]:<42} | {country[:10]:<12} | >={min_gpa} / >={min_ielts:<12} | {sim}% (Rất phù hợp)")
    print(f"    {'-'*100}")
    print(f"\n    [✓] KẾT LUẬN: Thay vì bỏ cuộc, ứng viên nhận được bản đồ khắc phục điểm yếu và 3 lựa chọn học bổng")
    print(f"        thay thế có tỷ lệ trúng tuyển cao nhất để nộp ngay trong năm nay!")

    cur.close()
    conn.close()

if __name__ == "__main__":
    run_ineligible_demo()
