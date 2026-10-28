"""
TRUY VẤN SO KHỚP VÀ XẾP HẠNG HỌC BỔNG TRỰC TIẾP TỪ SUPABASE (PGVECTOR)
Kết hợp Vector Semantic Similarity + Điểm sức mạnh chỉ số (GPA, IELTS, Papers, Awards)
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

def query_recommendations_for_candidate(candidate: dict, top_k: int = 5):
    print(f"\n[+] Đang kết nối tới Supabase PostgreSQL...")
    conn = psycopg2.connect(SUPABASE_URL)
    cur = conn.cursor()

    # 1. Tạo đoạn văn bản mô tả ứng viên và sinh vector 1536 chiều
    cand_text = (
        f"Candidate: {candidate['name']}. Degree Target: {candidate['degree_target']}. "
        f"Major: {candidate['major']}. Research Interest: {candidate['research_interest']}. "
        f"Experience: {candidate['work_exp_years']} years. "
        f"Research Papers: {candidate['research_papers']} publications, {candidate['awards']} awards."
    )
    cand_vector = generate_mock_vector_1536(cand_text)

    # 2. Tính điểm Profile Strength Score của ứng viên (Thang 0 - 100)
    gpa_score = min(max(candidate["gpa"] / 4.0, 0.0), 1.0) * 30.0
    ielts_score = min(max(candidate["ielts"] - 4.5, 0.0) / 4.5, 1.0) * 25.0
    exp_score = min(candidate["work_exp_years"] / 5.0, 1.0) * 15.0
    papers_score = min(candidate["research_papers"] * 3.5, 15.0)
    awards_score = min(candidate["awards"] * 2.5, 15.0)
    profile_strength = round(gpa_score + ielts_score + exp_score + papers_score + awards_score, 2)

    print(f"[+] Hồ sơ ứng viên: {candidate['name']}")
    print(f"    - GPA: {candidate['gpa']}/4.0 | IELTS: {candidate['ielts']} | NCKH: {candidate['research_papers']} bài báo | Giải thưởng: {candidate['awards']}")
    print(f"    - Điểm sức mạnh hồ sơ (Profile Strength): {profile_strength}/100 điểm")

    # 3. Truy vấn Vector Similarity + Xếp hạng trực tiếp trên Supabase
    vec_json = json.dumps(cand_vector)
    sql_query = """
    SELECT 
        id,
        title,
        source_name,
        host_country,
        degree_level,
        min_gpa,
        min_ielts,
        min_work_exp_years,
        funding_details,
        deadline,
        link,
        ROUND(((1.0 - (embedding <=> %s::vector)) * 100.0)::numeric, 2) AS sim_pct
    FROM scholarships
    ORDER BY embedding <=> %s::vector ASC
    LIMIT 20;
    """

    cur.execute(sql_query, [vec_json, vec_json])
    rows = cur.fetchall()

    print("\n" + "=" * 125)
    print(f"{'TOP':<4} | {'TÊN HỌC BỔNG':<38} | {'NGUỒN':<15} | {'HẠN NỘP':<14} | {'YÊU CẦU':<14} | {'ĐIỂM':<8} | {'TRẠNG THÁI'}")
    print("=" * 125)

    ranked_results = []
    for r in rows:
        sch_id, title, source_name, country, degree, min_gpa, min_ielts, min_exp, funding, deadline, link, sim_pct = r
        min_gpa = float(min_gpa or 3.0)
        min_ielts = float(min_ielts or 6.0)
        min_exp = float(min_exp or 0.0)

        is_eligible = True
        penalty = 0.0
        gaps = []

        if candidate["gpa"] < min_gpa:
            is_eligible = False
            penalty += 25.0
            gaps.append(f"Thiếu GPA ({candidate['gpa']} < {min_gpa})")

        if candidate["ielts"] < min_ielts:
            is_eligible = False
            penalty += 20.0
            gaps.append(f"Thiếu IELTS ({candidate['ielts']} < {min_ielts})")

        if candidate["work_exp_years"] < min_exp:
            is_eligible = False
            penalty += 15.0
            gaps.append(f"Thiếu KN ({candidate['work_exp_years']} < {min_exp} năm)")

        # Final Composite Ranking: 40% Vector Match + 60% Profile Strength - Penalty
        final_score = round(max(0.40 * float(sim_pct) + 0.60 * profile_strength - penalty, 0.0), 2)

        ranked_results.append({
            "title": title[:35] + "..." if len(title) > 35 else title,
            "source": (source_name or "Chính thức")[:14],
            "deadline": str(deadline or "Chưa rõ")[:13],
            "country": country[:10] if country else "Quốc tế",
            "req": f">={min_gpa} / >={min_ielts}",
            "sim_pct": f"{sim_pct}%",
            "final_score": final_score,
            "is_eligible": is_eligible,
            "gaps": gaps,
            "link": link
        })

    # Sắp xếp ưu tiên: Đạt chuẩn trước, điểm cao xếp trên
    ranked_results.sort(key=lambda x: (x["is_eligible"], x["final_score"]), reverse=True)

    for idx, item in enumerate(ranked_results[:top_k], 1):
        status = "ĐẠT CHUẨN" if item["is_eligible"] else f"CHƯA ĐẠT ({', '.join(item['gaps'])})"
        print(f"{idx:<4} | {item['title']:<38} | {item['source']:<15} | {item['deadline']:<14} | {item['req']:<14} | {item['final_score']:<8} | {status}")

    print("=" * 125)
    cur.close()
    conn.close()

if __name__ == "__main__":
    sample_candidate = {
        "name": "Nguyễn Trọng Mạnh Tiến",
        "degree_target": "Thạc sĩ",
        "major": "Khoa học Máy tính / Trí tuệ Nhân tạo",
        "research_interest": "Deep Learning, Natural Language Processing, Audio and Speech Processing",
        "gpa": 3.45,
        "ielts": 7.0,
        "work_exp_years": 1.5,
        "research_papers": 2,
        "awards": 2
    }

    query_recommendations_for_candidate(sample_candidate, top_k=5)
