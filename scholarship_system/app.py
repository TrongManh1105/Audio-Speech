"""
FLASK BACKEND CHO HỆ THỐNG GỢI Ý HỌC BỔNG & PHÂN TÍCH TIÊU CHÍ (GAP ANALYSIS)
Kết nối trực tiếp Supabase PostgreSQL + pgvector
"""

import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

import os
import json
import re
import psycopg2
from flask import Flask, render_template, request, jsonify
from supabase_importer import generate_mock_vector_1536

app = Flask(__name__)

SUPABASE_URL = os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_URL", "postgresql://postgres.wzsztxegmqeuwgozlggt:Trongmanh1102205@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres")

def format_deadline(dl_str):
    if not dl_str:
        return "Theo thông báo tuyển sinh chính thức"
    dl_str = str(dl_str).strip()
    
    # ISO date format: 2026-11-30T16:59:59.999Z or 2026-12-31
    m_iso = re.search(r"^(\d{4})-(\d{1,2})-(\d{1,2})", dl_str)
    if m_iso:
        return f"{m_iso.group(3).zfill(2)}/{m_iso.group(2).zfill(2)}/{m_iso.group(1)}"
        
    # Standard JS Date string: Fri Oct 30 2026
    month_map = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    m_js = re.search(r"([A-Za-z]{3})\s+([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})", dl_str)
    if m_js:
        day = m_js.group(3).zfill(2)
        month = month_map.get(m_js.group(2), "01")
        year = m_js.group(4)
        return f"{day}/{month}/{year}"
        
    # English date format: 1 Apr 2016 (annual)
    m_eng = re.search(r"(\d{1,2})\s+([A-Za-z]{3,9})\s+(\d{4})", dl_str)
    if m_eng:
        day = m_eng.group(1).zfill(2)
        mon_key = m_eng.group(2)[:3].capitalize()
        month = month_map.get(mon_key, "01")
        year = m_eng.group(3)
        extra = " (Hằng năm)" if "annual" in dl_str.lower() else ""
        return f"{day}/{month}/{year}{extra}"
        
    return dl_str

def get_db_connection():
    try:
        conn = psycopg2.connect(SUPABASE_URL, connect_timeout=6)
        return conn
    except Exception as e:
        print(f"[-] Lỗi kết nối Supabase: {e}")
        return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/match", methods=["POST"])
def match_scholarships():
    try:
        data = request.json or {}
        name = data.get("name", "Ứng viên")
        degree_target = data.get("degree_target", "Thạc sĩ")
        major = data.get("major", "Khoa học Máy tính / Công nghệ Thông tin")
        research_interest = data.get("research_interest", "Trí tuệ nhân tạo, Học sâu, Xử lý ngôn ngữ tự nhiên")
        
        gpa = float(data.get("gpa", 3.2))
        ielts = float(data.get("ielts", 6.5))
        work_exp = float(data.get("work_exp_years", 1.0))
        papers = int(data.get("research_papers", 0))
        awards = int(data.get("awards", 0))

        # 1. TÍNH ĐIỂM SỨC MẠNH HỒ SƠ (PROFILE STRENGTH - THANG 100)
        gpa_score = min(max(gpa / 4.0, 0.0), 1.0) * 30.0
        ielts_score = min(max(ielts - 4.5, 0.0) / 4.5, 1.0) * 25.0
        exp_score = min(work_exp / 5.0, 1.0) * 15.0
        papers_score = min(papers * 3.5, 15.0)
        awards_score = min(awards * 2.5, 15.0)
        profile_strength = round(gpa_score + ielts_score + exp_score + papers_score + awards_score, 2)

        # 2. TẠO VECTOR ĐỊNH HƯỚNG CỦA ỨNG VIÊN
        cand_text = (
            f"Candidate: {name}. Target: {degree_target}. Major: {major}. "
            f"Research Interest: {research_interest}. Experience: {work_exp} years, "
            f"{papers} papers, {awards} awards."
        )
        cand_vector = generate_mock_vector_1536(cand_text)
        vec_json = json.dumps(cand_vector)

        conn = get_db_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "Không thể kết nối đến cơ sở dữ liệu Supabase."
            }), 500

        cur = conn.cursor()

        # 3. LƯU TỰ ĐỘNG VÀO BẢNG candidate_profiles TRÊN SUPABASE
        try:
            insert_cand_sql = """
            INSERT INTO candidate_profiles (
                full_name, target_degree, major, gpa, ielts_score,
                work_exp_years, research_papers_count, awards_count,
                profile_summary, embedding
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s::vector)
            RETURNING id;
            """
            cur.execute(insert_cand_sql, (
                name, degree_target, major, gpa, ielts,
                work_exp, papers, awards, research_interest, vec_json
            ))
            saved_candidate_id = cur.fetchone()[0]
            conn.commit()
        except Exception as e:
            print(f"[!] Bỏ qua lưu profile: {e}")
            conn.rollback()
            saved_candidate_id = "temp-id"

        # 4. TRUY VẤN SO KHỚP VECTOR VÀ XẾP HẠNG HỌC BỔNG
        query_sql = """
        SELECT 
            id, title, source_name, host_country, degree_level, major_applied,
            funding_type, funding_details, min_gpa, min_ielts, min_work_exp_years,
            checklist, commitment, deadline, link,
            ROUND(((1.0 - (embedding <=> %s::vector)) * 100.0)::numeric, 2) AS sim_pct
        FROM scholarships
        ORDER BY embedding <=> %s::vector ASC
        LIMIT 25;
        """
        cur.execute(query_sql, [vec_json, vec_json])
        rows = cur.fetchall()

        matched_scholarships = []
        ineligible_list = []

        for r in rows:
            (sch_id, title, source_name, country, degree, major,
             funding_type, funding, min_gpa, min_ielts, min_exp,
             checklist, commitment, deadline, link, sim_pct) = r

            min_gpa = float(min_gpa or 3.0)
            min_ielts = float(min_ielts or 6.0)
            min_exp = float(min_exp or 0.0)

            is_eligible = True
            penalty = 0.0
            gaps = []

            if gpa < min_gpa:
                is_eligible = False
                penalty += 25.0
                gaps.append({
                    "field": "GPA",
                    "delta": round(min_gpa - gpa, 2),
                    "text": f"GPA hiện tại {gpa}/4.0 < Ngưỡng yêu cầu {min_gpa}/4.0"
                })

            if ielts < min_ielts:
                is_eligible = False
                penalty += 20.0
                gaps.append({
                    "field": "IELTS",
                    "delta": round(min_ielts - ielts, 1),
                    "text": f"IELTS hiện tại {ielts} < Ngưỡng yêu cầu {min_ielts}"
                })

            if work_exp < min_exp:
                is_eligible = False
                penalty += 15.0
                gaps.append({
                    "field": "Kinh nghiệm",
                    "delta": round(min_exp - work_exp, 1),
                    "text": f"Kinh nghiệm {work_exp} năm < Yêu cầu {min_exp} năm"
                })

            sim_val = float(sim_pct or 0.0)
            final_score = round(max(0.40 * sim_val + 0.60 * profile_strength - penalty, 0.0), 2)

            item = {
                "id": str(sch_id),
                "title": title,
                "source_name": source_name or "Chính thức",
                "country": country or "Quốc tế",
                "degree": degree or "Đa bậc học",
                "major": major or "Mọi ngành",
                "funding_type": funding_type or "Toàn phần",
                "funding": funding or "Toàn phần / Trợ cấp",
                "min_gpa": min_gpa,
                "min_ielts": min_ielts,
                "min_work_exp": min_exp,
                "checklist": checklist or "Bảng điểm, CV, Thư giới thiệu (LOR), SOP",
                "commitment": commitment or "Theo quy định của chương trình học bổng",
                "deadline": format_deadline(deadline),
                "link": link or "#",
                "sim_pct": sim_val,
                "final_score": final_score,
                "is_eligible": is_eligible,
                "gaps": gaps
            }

            if is_eligible:
                matched_scholarships.append(item)
            else:
                ineligible_list.append(item)

        # Sắp xếp danh sách đạt chuẩn: điểm cao nhất lên Top 1
        matched_scholarships.sort(key=lambda x: x["final_score"], reverse=True)
        ineligible_list.sort(key=lambda x: x["sim_pct"], reverse=True)

        # Toàn bộ ID của các học bổng đã xét duyệt ở mục mục tiêu (bao gồm cả Đạt và Bị loại)
        target_ids = list(set([m["id"] for m in matched_scholarships] + [m["id"] for m in ineligible_list]))
        if not target_ids:
            target_ids = ["00000000-0000-0000-0000-000000000000"]

        # 5. SINH LỘ TRÌNH NẾU ỨNG VIÊN BỊ TRƯỢT HOẶC CÓ TIÊU CHÍ THIẾU
        roadmap = []
        overall_status = "ELIGIBLE" if len(matched_scholarships) > 0 else "INELIGIBLE"

        # Tổng hợp các GAP nặng nhất
        top_ineligible = ineligible_list[0] if ineligible_list else None
        gap_summary = []

        if top_ineligible and top_ineligible["gaps"]:
            gap_summary = top_ineligible["gaps"]
            
            # Giai đoạn ngoại ngữ
            ielts_gaps = [g for g in gap_summary if g["field"] == "IELTS"]
            if ielts_gaps:
                delta = ielts_gaps[0]["delta"]
                roadmap.append({
                    "stage": "Giai đoạn 1: Nâng chuẩn ngoại ngữ (3-4 tháng)",
                    "title": f"Luyện thi cấp tốc nâng +{delta} band IELTS",
                    "action": f"Đăng ký ôn luyện chuyên sâu kỹ năng Writing và Speaking để đạt mốc {ielts + delta} kịp đợt nộp hồ sơ tới."
                })

            # Giai đoạn GPA & Điểm cộng NCKH
            gpa_gaps = [g for g in gap_summary if g["field"] == "GPA"]
            if gpa_gaps:
                roadmap.append({
                    "stage": "Giai đoạn 2: Chiến lược bù trừ học thuật",
                    "title": "Bù trừ điểm GPA bằng bài báo khoa học",
                    "action": "Tham gia lab nghiên cứu viết 01 bài báo (Conference/Scopus) và hoàn thành các chứng chỉ chuyên ngành quốc tế để làm đẹp hồ sơ."
                })

            # Giai đoạn kinh nghiệm
            exp_gaps = [g for g in gap_summary if g["field"] == "Kinh nghiệm"]
            if exp_gaps:
                delta = exp_gaps[0]["delta"]
                roadmap.append({
                    "stage": "Giai đoạn 3: Tích lũy thâm niên làm việc",
                    "title": f"Tích lũy thêm {delta} năm công tác",
                    "action": "Làm việc toàn thời gian trong lĩnh vực liên quan và xin Thư giới thiệu (LOR) từ cấp quản lý trực tiếp."
                })

        # Giai đoạn hoàn thiện hồ sơ luôn có
        roadmap.append({
            "stage": "Giai đoạn cuối: Hoàn thiện hồ sơ & Phỏng vấn",
            "title": "Soạn bài luận cá nhân (SOP) & Portfolio",
            "action": "Viết Statement of Purpose nhấn mạnh vào tiềm năng đóng góp và luyện phỏng vấn thử (Mock Interview)."
        })

        # 6. TRUY VẤN CÁC HỌC BỔNG DỰ PHÒNG VỪA SỨC (SAFETY ALTERNATIVES)
        # NGUYÊN TẮC:
        # 1. Điều kiện sàn BẮT BUỘC THẤP HƠN HOẶC BẰNG (<=) so với hồ sơ ứng viên nhập.
        # 2. TUYỆT ĐỐI KHÔNG TRÙNG với bất kỳ học bổng nào đã xét duyệt ở mục mục tiêu (target_ids).
        # 3. Ưu tiên theo độ tương đồng chuyên môn (Vector Embeddings).
        sql_safety = """
        SELECT 
            id, title, source_name, host_country, degree_level, major_applied,
            funding_type, funding_details, min_gpa, min_ielts, min_work_exp_years,
            checklist, commitment, deadline, link,
            ROUND(((1.0 - (embedding <=> %s::vector)) * 100.0)::numeric, 2) AS sim_pct
        FROM scholarships
        WHERE is_active = TRUE
          AND (min_gpa IS NULL OR min_gpa <= %s)
          AND (min_ielts IS NULL OR min_ielts <= %s)
          AND (min_work_exp_years IS NULL OR min_work_exp_years <= %s)
          AND id::text != ALL(%s)
        ORDER BY embedding <=> %s::vector ASC
        LIMIT 6;
        """
        cur.execute(sql_safety, [vec_json, gpa, ielts, work_exp, target_ids, vec_json])
        safety_rows = cur.fetchall()

        safety_alternatives = []
        for r in safety_rows:
            (sch_id, title, source_name, country, degree, major,
             funding_type, funding, sch_min_gpa, sch_min_ielts, sch_min_exp,
             checklist, commitment, deadline, link, sim_pct) = r
            safety_alternatives.append({
                "id": str(sch_id),
                "title": title,
                "source_name": source_name or "Chính thức",
                "country": country or "Quốc tế",
                "degree": degree or "Đa bậc học",
                "major": major or "Mọi ngành",
                "funding_type": funding_type or "Toàn phần",
                "funding": funding or "Toàn phần / Trợ cấp",
                "min_gpa": float(sch_min_gpa or 0.0),
                "min_ielts": float(sch_min_ielts or 0.0),
                "min_work_exp": float(sch_min_exp or 0.0),
                "checklist": checklist or "Bảng điểm, CV, Thư giới thiệu (LOR), SOP",
                "commitment": commitment or "Theo quy định học bổng",
                "deadline": format_deadline(deadline),
                "link": link or "#",
                "sim_pct": float(sim_pct or 0.0),
                "is_satisfied": True
            })

        cur.close()
        conn.close()



        return jsonify({
            "status": "success",
            "candidate": {
                "name": name,
                "profile_strength": profile_strength,
                "overall_status": overall_status,
                "saved_id": str(saved_candidate_id)
            },
            "matched_scholarships": matched_scholarships[:6],
            "ineligible_scholarships": ineligible_list[:4],
            "gap_summary": gap_summary,
            "roadmap": roadmap,
            "safety_alternatives": safety_alternatives
        })

    except Exception as e:
        print(f"[-] Lỗi xử lý matching: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[+] Khởi chạy Web Server tại: http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

