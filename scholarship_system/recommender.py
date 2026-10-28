"""
Scholarship Recommendation & Gap Analysis Engine (Phiên bản nâng cao với 16 trường chi tiết)
So khớp hồ sơ ứng viên với các tiêu chí chuyên sâu và đề xuất kế hoạch hành động cụ thể.
"""

import csv
import os
import sys
import re
from typing import Dict, Any, List

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "all_scholarships_combined.csv")

def parse_min_gpa(gpa_str: str) -> float:
    """Trích xuất ngưỡng GPA tối thiểu (quy đổi về thang 4.0)"""
    if not gpa_str:
        return 3.0
    match_4 = re.search(r"(\d+\.\d+)\s*/\s*4\.0", gpa_str)
    if match_4:
        return float(match_4.group(1))
    match_10 = re.search(r"(\d+\.?\d*)\s*/\s*10", gpa_str)
    if match_10:
        val = float(match_10.group(1))
        # Quy đổi tương đương 10 sang 4.0
        return round((val / 10.0) * 4.0, 2)
    match_pct = re.search(r"(\d+)%", gpa_str)
    if match_pct:
        pct = float(match_pct.group(1))
        return round((pct / 100.0) * 4.0, 2)
    return 3.0

def parse_min_ielts(ielts_str: str) -> float:
    """Trích xuất ngưỡng IELTS tối thiểu"""
    if not ielts_str:
        return 6.0
    match = re.search(r"IELTS[^\d]*(\d+\.?\d*)", ielts_str, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return 6.0

def evaluate_scholarship_match(profile: Dict[str, Any], scholarship: Dict[str, str]) -> Dict[str, Any]:
    score = 0
    gaps = []
    strengths = []
    is_eligible = True
    
    title = scholarship.get("Tên học bổng", "")
    country = scholarship.get("Quốc gia", "")
    degree = scholarship.get("Bậc học", "")
    major_applied = scholarship.get("Chuyên ngành áp dụng", "")
    min_gpa_text = scholarship.get("GPA tối thiểu", "")
    ielts_text = scholarship.get("Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)", "")
    work_exp_text = scholarship.get("Kinh nghiệm làm việc yêu cầu", "")
    age_limit_text = scholarship.get("Độ tuổi giới hạn", "")
    checklist = scholarship.get("Hồ sơ cần chuẩn bị (Checklist)", "")
    commitment = scholarship.get("Ràng buộc & Cam kết", "")
    deadline = scholarship.get("Hạn nộp & Chu kỳ tuyển sinh", "")
    apply_method = scholarship.get("Phương thức ứng tuyển", "")
    funding_detail = scholarship.get("Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)", "")
    link = scholarship.get("Link chi tiết", "")

    # 1. BẬC HỌC (Weight: 25 pts)
    user_degree = profile.get("degree_target", "Thạc sĩ").lower()
    if user_degree in degree.lower() or "tất cả" in degree.lower():
        score += 25
        strengths.append(f"Khớp đúng bậc học mong muốn ({profile.get('degree_target')})")
    else:
        score += 10
        gaps.append(f"Bậc học không khớp: Học bổng dành cho '{degree}'")

    # 2. QUỐC GIA ƯU TIÊN (Weight: 15 pts)
    user_country = profile.get("preferred_country", "").lower()
    if user_country and (user_country in country.lower() or "quốc tế" in country.lower()):
        score += 15
        strengths.append(f"Điểm đến học tập khớp nguyện vọng ({country})")
    else:
        score += 8

    # 3. GPA HỌC TẬP (Weight: 20 pts)
    user_gpa = profile.get("gpa", 3.2)
    min_gpa_val = parse_min_gpa(min_gpa_text)
    if user_gpa >= min_gpa_val:
        score += 20
        strengths.append(f"GPA {user_gpa}/4.0 vượt ngưỡng tối thiểu yêu cầu ({min_gpa_text})")
    else:
        # Nếu thấp hơn ngưỡng tối thiểu của học bổng nghiêm ngặt
        if "chevening" in title.lower() or "gks" in title.lower() or "bắt buộc" in min_gpa_text.lower():
            is_eligible = False
            gaps.append(f"CHƯA ĐẠT GPA: Yêu cầu tối thiểu {min_gpa_text}, hiện tại bạn đạt {user_gpa}/4.0")
        else:
            score += 8
            gaps.append(f"GPA ({user_gpa}) thấp hơn mức cạnh tranh khuyến nghị ({min_gpa_text})")

    # 4. NGOẠI NGỮ (Weight: 20 pts)
    user_ielts = profile.get("ielts", 6.5)
    min_ielts_val = parse_min_ielts(ielts_text)
    user_topik = profile.get("topik_level", 0)
    
    if "topik" in ielts_text.lower() and user_topik >= 3:
        score += 20
        strengths.append(f"Có chứng chỉ tiếng Hàn TOPIK {user_topik} - Lợi thế vượt trội cho học bổng Hàn Quốc")
    elif user_ielts >= min_ielts_val:
        score += 20
        strengths.append(f"Chứng chỉ IELTS {user_ielts} đáp ứng tốt chuẩn yêu cầu ({ielts_text})")
    else:
        deficit = round(min_ielts_val - user_ielts, 1)
        score += 8
        gaps.append(f"CẦN NÂNG ĐIỂM TIẾNG ANH: Hiện tại IELTS {user_ielts}, cần nâng thêm tối thiểu {deficit} band để đạt {min_ielts_val}")

    # 5. KINH NGHIỆM LÀM VIỆC (Weight: 20 pts)
    user_exp_years = profile.get("work_experience_years", 1.0)
    if "bắt buộc" in work_exp_text.lower() or "2 năm" in work_exp_text.lower() or "2,800 giờ" in work_exp_text:
        if user_exp_years >= 2.0:
            score += 20
            strengths.append(f"Kinh nghiệm làm việc ({user_exp_years} năm) thỏa mãn điều kiện bắt buộc")
        else:
            is_eligible = False
            needed = round(2.0 - user_exp_years, 1)
            gaps.append(f"CHƯA ĐỦ KINH NGHIỆM: Học bổng bắt buộc tối thiểu 2 năm kinh nghiệm. Bạn còn thiếu khoảng {needed} năm")
    elif "1 năm" in work_exp_text.lower():
        if user_exp_years >= 1.0:
            score += 20
            strengths.append(f"Thỏa mãn yêu cầu kinh nghiệm làm việc ({work_exp_text})")
        else:
            gaps.append(f"Ưu tiên tích lũy thêm kinh nghiệm làm việc ({work_exp_text})")
    else:
        score += 20
        strengths.append(f"Không yêu cầu ràng buộc về kinh nghiệm làm việc")

    # PHÂN LOẠI TRẠNG THÁI
    if not is_eligible:
        status = "CHƯA ĐẠT ĐIỀU KIỆN BẮT BUỘC (Ineligible)"
    elif score >= 85:
        status = "RẤT PHÙ HỢP / ĐẠT TIÊU CHÍ (High Match - Top Choice)"
    elif score >= 70:
        status = "KHẢ THI CÓ ĐIỀU KIỆN (Moderate Match)"
    else:
        status = "CẠNH TRANH THẤP (Low Match)"

    return {
        "title": title,
        "source": scholarship.get("Nguồn"),
        "country": country,
        "degree": degree,
        "major_applied": major_applied,
        "funding": scholarship.get("Mức tài trợ"),
        "funding_detail": funding_detail,
        "score": score,
        "is_eligible": is_eligible,
        "status": status,
        "strengths": strengths,
        "gaps": gaps,
        "min_gpa_text": min_gpa_text,
        "ielts_text": ielts_text,
        "work_exp_text": work_exp_text,
        "age_limit_text": age_limit_text,
        "checklist": checklist,
        "commitment": commitment,
        "deadline": deadline,
        "apply_method": apply_method,
        "link": link
    }

def recommend_scholarships(profile: Dict[str, Any], top_k: int = 5) -> List[Dict[str, Any]]:
    if not os.path.exists(DATA_FILE):
        return []
    records = []
    with open(DATA_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    evaluated = [evaluate_scholarship_match(profile, r) for r in records]
    # Sắp xếp: Ưu tiên ứng viên đủ điều kiện trước, sau đó sắp xếp theo score giảm dần
    evaluated.sort(key=lambda x: (x["is_eligible"], x["score"]), reverse=True)
    return evaluated[:top_k]

if __name__ == "__main__":
    profile = {
        "candidate_name": "Nguyễn Trọng Mạnh Tiến",
        "degree_target": "Thạc sĩ",
        "gpa": 3.4,                  # Thang 4.0
        "ielts": 6.5,
        "topik_level": 3,
        "work_experience_years": 1.5,
        "preferred_country": "Hàn Quốc",
        "major": "Khoa học Máy tính / Trí tuệ Nhân tạo"
    }

    print("\n" + "="*85)
    print(f"KẾT QUẢ PHÂN TÍCH TIÊU CHÍ CHI TIẾT CHO ỨNG VIÊN: {profile['candidate_name'].upper()}")
    print("="*85)
    
    results = recommend_scholarships(profile, top_k=5)
    for idx, r in enumerate(results, start=1):
        print(f"\n[{idx}] {r['title']} ({r['score']}/100 ĐIỂM) - {r['status']}")
        print(f"    * Nguồn: {r['source']} | Quốc gia: {r['country']} | Bậc học: {r['degree']}")
        print(f"    * Quyền lợi: {r['funding_detail']}")
        print(f"    * Hạn nộp & Phương thức: {r['deadline']} ({r['apply_method']})")
        print(f"    * Tiêu chuẩn: GPA {r['min_gpa_text']} | Ngoại ngữ: {r['ielts_text']} | Kinh nghiệm: {r['work_exp_text']}")
        if r["strengths"]:
            print(f"    [+] Mục đã đạt:")
            for s in r["strengths"]:
                print(f"        ✓ {s}")
        if r["gaps"]:
            print(f"    [-] CẦN BỔ SUNG / CẢI THIỆN ĐỂ ĐẠT:")
            for g in r["gaps"]:
                print(f"        ! {g}")
        print(f"    * Danh mục hồ sơ cần nộp (Checklist): {r['checklist']}")
        print(f"    * Ràng buộc & Cam kết: {r['commitment']}")
        print(f"    * Link chính thức: {r['link']}")
