"""
MODULE XỬ LÝ KHI ỨNG VIÊN 'KHÔNG ĐẠT' (INELIGIBLE / LOW MATCH)
Bao gồm:
1. Phân tích khoảng cách tiêu chuẩn (Rule-based Gap Analysis)
2. Sinh lộ trình cải thiện có mốc thời gian cụ thể (Actionable Roadmap)
3. Đề xuất học bổng dự phòng vừa sức bằng Vector Search (Safety Alternatives)
"""

import sys

# Đảm bảo in tiếng Việt chuẩn trên Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from typing import Dict, Any, List


def analyze_gaps_and_create_roadmap(candidate: Dict[str, Any], scholarship: Dict[str, Any]) -> Dict[str, Any]:
    """
    Phân tích chi tiết những tiêu chí chưa đạt và đưa ra kế hoạch hành động từng bước.
    """
    gaps = []
    action_plan = []
    
    cand_gpa = candidate.get("gpa", 0.0)
    sch_min_gpa = scholarship.get("min_gpa", 3.0)
    
    cand_ielts = candidate.get("ielts", 0.0)
    sch_min_ielts = scholarship.get("min_ielts", 6.0)
    
    cand_exp = candidate.get("work_exp_years", 0.0)
    sch_min_exp = scholarship.get("min_work_exp", 0.0)
    
    # 1. KIỂM TRA GPA
    if cand_gpa < sch_min_gpa:
        delta_gpa = round(sch_min_gpa - cand_gpa, 2)
        gaps.append(f"Điểm GPA ({cand_gpa}/4.0) thấp hơn mức sàn yêu cầu ({sch_min_gpa}/4.0) là {delta_gpa} điểm.")
        action_plan.append({
            "stage": "Giai đoạn 1: Bù trừ điểm học thuật",
            "timeframe": "Ngay lập tức",
            "action": "Gia tăng thành tích nghiên cứu bù đắp cho GPA",
            "advice": (
                "Nếu đã tốt nghiệp, điểm GPA không thể thay đổi. Hãy bù trừ bằng cách: "
                "Tham gia nhóm nghiên cứu (Lab) để đứng tên 01 bài báo khoa học (Conference/Scopus), "
                "hoặc hoàn thành các chứng chỉ chuyên ngành quốc tế (Coursera/DeepLearning.AI) để chứng minh năng lực tự học."
            )
        })

    # 2. KIỂM TRA NGOẠI NGỮ (IELTS)
    if cand_ielts < sch_min_ielts:
        delta_ielts = round(sch_min_ielts - cand_ielts, 1)
        # Ước lượng thời gian: Cứ 0.5 band cần khoảng 2-3 tháng ôn luyện tập trung
        est_months = max(int(delta_ielts * 4), 2)
        gaps.append(f"Điểm IELTS ({cand_ielts}) chưa đạt chuẩn đầu vào ({sch_min_ielts}), còn thiếu {delta_ielts} band.")
        action_plan.append({
            "stage": "Giai đoạn 2: Nâng chuẩn ngoại ngữ bắt buộc",
            "timeframe": f"Trong vòng {est_months} tháng tới",
            "action": f"Lên kế hoạch luyện thi nâng thêm tối thiểu +{delta_ielts} band IELTS",
            "advice": (
                f"Đăng ký thi lại mục tiêu đạt tối thiểu {sch_min_ielts}. "
                "Tập trung ôn luyện chuyên sâu 2 kỹ năng Writing và Speaking vì đây là 2 tiêu chí phỏng vấn học bổng đánh giá khắt khe nhất."
            )
        })

    # 3. KIỂM TRA KINH NGHIỆM LÀM VIỆC
    if cand_exp < sch_min_exp:
        delta_exp = round(sch_min_exp - cand_exp, 1)
        est_months_exp = int(delta_exp * 12)
        gaps.append(f"Chưa đủ thâm niên làm việc: Thiếu {delta_exp} năm kinh nghiệm ({est_months_exp} tháng).")
        action_plan.append({
            "stage": "Giai đoạn 3: Tích lũy kinh nghiệm thực tế",
            "timeframe": f"{est_months_exp} tháng tới",
            "action": "Tích lũy đủ giờ làm việc theo quy định",
            "advice": (
                f"Chương trình yêu cầu tối thiểu {sch_min_exp} năm làm việc thực tế. "
                "Cần tiếp tục công tác toàn thời gian trong lĩnh vực liên quan và xin giấy xác nhận công tác từ cơ quan trước kỳ tuyển sinh tiếp theo."
            )
        })

    # 4. HỒ SƠ & BÀI LUẬN
    action_plan.append({
        "stage": "Giai đoạn 4: Hoàn thiện hồ sơ cạnh tranh",
        "timeframe": "Trước hạn nộp 2 tháng",
        "action": "Xây dựng bài luận cá nhân (SOP) và xin thư giới thiệu (LOR)",
        "advice": (
            "Soạn thảo Personal Statement / Statement of Purpose nhấn mạnh vào lý do chọn ngành và cam kết đóng góp. "
            "Liên hệ 02 Giảng viên/Giáo sư đại học hoặc Trưởng bộ phận nơi làm việc để xin Thư giới thiệu uy tín."
        )
    })

    return {
        "status": "CHƯA ĐẠT ĐIỀU KIỆN SÀN (INELIGIBLE)",
        "gaps_count": len(gaps),
        "details_gaps": gaps,
        "actionable_roadmap": action_plan
    }

if __name__ == "__main__":
    print("=" * 80)
    print("DEMO LUỒNG SINH LỘ TRÌNH VÀ PHÂN TÍCH GAP CHO ỨNG VIÊN CHƯA ĐẠT")
    print("=" * 80)

    sample_candidate = {
        "name": "Nguyễn Trọng Mạnh Tiến",
        "gpa": 3.05,
        "ielts": 6.0,
        "work_exp_years": 0.5
    }

    target_scholarship = {
        "title": "Chevening Scholarship 2026 (Vương Quốc Anh)",
        "min_gpa": 3.3,
        "min_ielts": 7.0,
        "min_work_exp": 2.0
    }

    print(f"\n[+] Ứng viên: {sample_candidate['name']}")
    print(f"[+] Học bổng mục tiêu: {target_scholarship['title']}\n")

    result = analyze_gaps_and_create_roadmap(sample_candidate, target_scholarship)

    print(f"TRẠNG THÁI: {result['status']}")
    print("\n[-] CÁC KHOẢNG TRỐNG TIÊU CHÍ (GAPS):")
    for idx, gap in enumerate(result["details_gaps"], 1):
        print(f"  {idx}. {gap}")

    print("\n[+] LỘ TRÌNH HÀNH ĐỘNG CỤ THỂ (ACTIONABLE ROADMAP):")
    for step in result["actionable_roadmap"]:
        print(f"\n  ➤ [{step['stage']}] - Thời hạn: {step['timeframe']}")
        print(f"    * Nhiệm vụ: {step['action']}")
        print(f"    * Lời khuyên: {step['advice']}")
