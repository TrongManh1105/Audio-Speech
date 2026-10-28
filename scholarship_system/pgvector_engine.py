"""
PGVECTOR INTEGRATION PIPELINE CHO HỆ THỐNG GỢI Ý HỌC BỔNG
Giải pháp kết hợp Vector Embeddings (Semantic Match) và Multi-Factor Strength Scoring
(Ưu tiên ứng viên có các chỉ số cao và nhiều thành tích nhất lên Top 1).
"""

import math
import json
import csv
import os
import sys
from typing import List, Dict, Any, Tuple

# Đảm bảo in tiếng Việt chuẩn trên Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==============================================================================
# 1. ĐỊNH NGHĨA PROFILE ỨNG VIÊN & TIÊU CHÍ ĐỊNH LƯỢNG
# ==============================================================================
class CandidateProfile:
    def __init__(
        self,
        candidate_id: str,
        name: str,
        target_degree: str,
        major: str,
        gpa: float,                     # Thang 4.0
        ielts: float,                   # Thang 9.0
        topik: int = 0,                 # Thang 1 - 6
        work_exp_years: float = 0.0,
        research_papers: int = 0,       # Số lượng bài báo (Scopus / ISI / Conference)
        awards_count: int = 0,          # Số giải thưởng học thuật / thi đấu
        extracurricular_count: int = 0, # Hoạt động ngoại khóa / leadership
        research_interest: str = ""     # Định hướng nghiên cứu chuyên sâu
    ):
        self.candidate_id = candidate_id
        self.name = name
        self.target_degree = target_degree
        self.major = major
        self.gpa = gpa
        self.ielts = ielts
        self.topik = topik
        self.work_exp_years = work_exp_years
        self.research_papers = research_papers
        self.awards_count = awards_count
        self.extracurricular_count = extracurricular_count
        self.research_interest = research_interest

    def to_text_for_embedding(self) -> str:
        """Đoạn văn bản tóm tắt định hướng nghiên cứu và học thuật để tạo Vector"""
        return (
            f"Candidate: {self.name}. Degree Target: {self.target_degree}. Major: {self.major}. "
            f"Research Interest: {self.research_interest}. "
            f"Background: {self.work_exp_years} years experience in {self.major}, "
            f"{self.research_papers} published research papers, {self.awards_count} academic awards."
        )

    def calculate_profile_strength(self) -> float:
        """
        TÍNH ĐIỂM SỨC MẠNH HỒ SƠ (Profile Strength Score - Thang 0 đến 100)
        Nguyên tắc cốt lõi: Ứng viên có CHỈ SỐ CAO (GPA, IELTS) và NHIỀU (Papers, Awards)
        sẽ có điểm Profile Strength vượt trội.
        """
        # 1. GPA (Tối đa 30 điểm): Tỉ lệ thuận tuyến tính trên thang 4.0
        gpa_score = min(max(self.gpa / 4.0, 0.0), 1.0) * 30.0

        # 2. IELTS (Tối đa 25 điểm): Chuẩn hóa từ mốc 5.0 đến 9.0
        # IELTS >= 8.5 đạt max 25đ, IELTS 7.0 đạt ~16đ, IELTS 6.0 đạt ~10đ
        ielts_normalized = max(self.ielts - 4.5, 0.0) / 4.5
        ielts_score = min(ielts_normalized, 1.0) * 25.0

        # 3. Kinh nghiệm làm việc (Tối đa 15 điểm): Bão hòa ở mốc 5 năm
        exp_score = min(self.work_exp_years / 5.0, 1.0) * 15.0

        # 4. Số lượng bài báo khoa học (Tối đa 15 điểm): 3.5 điểm / bài báo
        # Càng nhiều bài báo điểm càng tiệm cận max
        papers_score = min(self.research_papers * 3.5, 15.0)

        # 5. Số lượng giải thưởng & Ngoại khóa (Tối đa 15 điểm): 2.5đ/giải + 1đ/ngoại khóa
        achieve_score = min(self.awards_count * 2.5 + self.extracurricular_count * 1.0, 15.0)

        total_strength = gpa_score + ielts_score + exp_score + papers_score + achieve_score
        return round(total_strength, 2)


# ==============================================================================
# 2. ĐỊNH NGHĨA CẤU TRÚC HỌC BỔNG ĐƯỢC CÀO VỀ (SCHOLARSHIP ITEM)
# ==============================================================================
class ScrapedScholarship:
    def __init__(
        self,
        scholarship_id: str,
        title: str,
        country: str,
        degree: str,
        major: str,
        min_gpa: float,
        min_ielts: float,
        min_work_exp: float,
        funding_detail: str,
        raw_description: str
    ):
        self.scholarship_id = scholarship_id
        self.title = title
        self.country = country
        self.degree = degree
        self.major = major
        self.min_gpa = min_gpa
        self.min_ielts = min_ielts
        self.min_work_exp = min_work_exp
        self.funding_detail = funding_detail
        self.raw_description = raw_description

    def to_text_for_embedding(self) -> str:
        """Tạo văn bản mô tả học bổng để sinh Vector Embedding trong PostgreSQL"""
        return (
            f"Scholarship: {self.title}. Country: {self.country}. Degree: {self.degree}. "
            f"Target Fields: {self.major}. Benefits: {self.funding_detail}. "
            f"Description: {self.raw_description}"
        )


# ==============================================================================
# 3. GIẢ LẬP VECTOR SIMILARITY (HOẶC GỌI EMBEDDING MODEL THỰC TẾ)
# Trong môi trường production, đây sẽ là vector sinh từ OpenAI hoặc BGE-M3
# ==============================================================================
def compute_mock_semantic_similarity(candidate_text: str, scholarship_text: str) -> float:
    """
    Giả lập độ tương đồng Cosine Similarity dựa trên semantic overlap (từ khóa và ngữ cảnh ngành học).
    Trả về giá trị từ 0.0 đến 1.0 (tương ứng 1 - cosine_distance trong pgvector).
    """
    cand_tokens = set(candidate_text.lower().replace(",", " ").replace(".", " ").split())
    sch_tokens = set(scholarship_text.lower().replace(",", " ").replace(".", " ").split())
    
    if not cand_tokens or not sch_tokens:
        return 0.5
    
    intersection = cand_tokens.intersection(sch_tokens)
    union = cand_tokens.union(sch_tokens)
    
    # Jaccard + Semantic Boost cho các từ khóa chuyên ngành
    base_sim = len(intersection) / len(union)
    
    # Tăng cường độ tương đồng nếu ngành học khớp nhau
    key_fields = ["ai", "computer science", "stem", "data", "machine learning", "trí tuệ nhân tạo"]
    for k in key_fields:
        if k in candidate_text.lower() and k in scholarship_text.lower():
            base_sim += 0.35
            break
            
    return min(max(base_sim * 2.0, 0.30), 0.98)


# ==============================================================================
# 4. CÔNG THỨC HYBRID RANKING: VECTOR MATCH + PROFILE STRENGTH
# ==============================================================================
def rank_candidates(
    scholarship: ScrapedScholarship,
    candidates: List[CandidateProfile],
    weight_semantic: float = 0.40,
    weight_strength: float = 0.60
) -> List[Dict[str, Any]]:
    """
    Xếp hạng danh sách ứng viên cho 1 học bổng cụ thể:
    - w_semantic (40%): Đảm bảo ứng viên có định hướng đúng ngành/chủ đề học bổng yêu cầu.
    - w_strength (60%): Ứng viên chỉ số CÀNG CAO (GPA, IELTS) & CÀNG NHIỀU (Papers, Awards)
      thì điểm càng vượt trội và xếp trên cùng.
    """
    ranked_list = []
    sch_embed_text = scholarship.to_text_for_embedding()

    for cand in candidates:
        cand_embed_text = cand.to_text_for_embedding()
        
        # 1. Điểm tương đồng Vector (Cosine Similarity quy ra thang 100)
        sim_ratio = compute_mock_semantic_similarity(cand_embed_text, sch_embed_text)
        semantic_score = round(sim_ratio * 100.0, 2)
        
        # 2. Điểm sức mạnh chỉ số định lượng (Thang 100)
        strength_score = cand.calculate_profile_strength()

        # 3. Kiểm tra điều kiện ngặt (Hard Filter / Penalty)
        is_eligible = True
        penalty = 0.0
        gaps = []

        if cand.gpa < scholarship.min_gpa:
            is_eligible = False
            penalty += 25.0
            gaps.append(f"GPA {cand.gpa} < {scholarship.min_gpa}")

        if cand.ielts < scholarship.min_ielts:
            is_eligible = False
            penalty += 20.0
            gaps.append(f"IELTS {cand.ielts} < {scholarship.min_ielts}")

        if cand.work_exp_years < scholarship.min_work_exp:
            is_eligible = False
            penalty += 15.0
            gaps.append(f"Kinh nghiệm {cand.work_exp_years} năm < {scholarship.min_work_exp} năm")

        # 4. Điểm tổng hợp cuối cùng (Final Composite Score)
        final_score = (weight_semantic * semantic_score) + (weight_strength * strength_score) - penalty
        final_score = round(max(final_score, 0.0), 2)

        ranked_list.append({
            "candidate_id": cand.candidate_id,
            "name": cand.name,
            "gpa": cand.gpa,
            "ielts": cand.ielts,
            "research_papers": cand.research_papers,
            "awards_count": cand.awards_count,
            "work_exp_years": cand.work_exp_years,
            "semantic_score": semantic_score,
            "strength_score": strength_score,
            "penalty": penalty,
            "final_score": final_score,
            "is_eligible": is_eligible,
            "gaps": gaps
        })

    # Sắp xếp: Điểm cao nhất lên Top 1, giảm dần
    ranked_list.sort(key=lambda x: (x["is_eligible"], x["final_score"]), reverse=True)
    return ranked_list


# ==============================================================================
# 5. DEMO THỰC TẾ SO SÁNH CÁC HỒ SƠ ỨNG VIÊN
# ==============================================================================
if __name__ == "__main__":
    print("=" * 95)
    print("MÔ PHỎNG THUẬT TOÁN XẾP HẠNG VECTOR + PROFILE STRENGTH TRONG POSTGRESQL (PGVECTOR)")
    print("=" * 95)

    # Giả sử đây là một học bổng cào về từ Scholars4dev / Chevening / NIIED Korea
    test_scholarship = ScrapedScholarship(
        scholarship_id="SCH-KOREA-GKS-01",
        title="Global Korea Scholarship (GKS) - Graduate Program 2026",
        country="Hàn Quốc",
        degree="Thạc sĩ",
        major="Computer Science, Artificial Intelligence, Data Engineering",
        min_gpa=3.2,
        min_ielts=6.5,
        min_work_exp=1.0,
        funding_detail="Học phí 100%, Trợ cấp sinh hoạt 1,000,000 KRW/tháng, Vé máy bay khứ hồi, Bảo hiểm y tế",
        raw_description="Chương trình học bổng chính phủ Hàn Quốc dành cho học viên thạc sĩ xuất sắc ngành AI & Khoa học máy tính."
    )

    # 4 ứng viên với các mức độ chỉ số khác nhau:
    candidates = [
        # Ứng viên 1: "Chỉ số cao và nhiều" (GPA khủng 3.9, IELTS 8.0, 3 bài báo quốc tế, 4 giải thưởng)
        CandidateProfile(
            candidate_id="CAND-01",
            name="Nguyễn Văn Xuất Sắc (Profile Khủng)",
            target_degree="Thạc sĩ",
            major="Computer Science / Artificial Intelligence",
            gpa=3.92,
            ielts=8.0,
            work_exp_years=2.5,
            research_papers=3,
            awards_count=4,
            extracurricular_count=3,
            research_interest="Nghiên cứu mô hình ngôn ngữ lớn (LLMs) và thị giác máy tính ứng dụng y tế"
        ),
        # Ứng viên 2: Chỉ số khá (GPA 3.4, IELTS 6.5, 1 bài báo, 1 giải thưởng)
        CandidateProfile(
            candidate_id="CAND-02",
            name="Trần Thị Khá Giỏi (Profile Tiêu Chuẩn)",
            target_degree="Thạc sĩ",
            major="Information Technology / Data Science",
            gpa=3.45,
            ielts=6.5,
            work_exp_years=1.5,
            research_papers=1,
            awards_count=1,
            extracurricular_count=2,
            research_interest="Học máy ứng dụng trong phân tích dữ liệu kinh doanh"
        ),
        # Ứng viên 3: Khớp từ khóa semantic nhưng chỉ số thành tích ít (GPA 3.25, IELTS 6.5, 0 bài báo, 0 giải)
        CandidateProfile(
            candidate_id="CAND-03",
            name="Lê Văn Cơ Bản (Profile Trung Bình)",
            target_degree="Thạc sĩ",
            major="Computer Science",
            gpa=3.22,
            ielts=6.5,
            work_exp_years=1.0,
            research_papers=0,
            awards_count=0,
            extracurricular_count=1,
            research_interest="Muốn du học Hàn Quốc học thạc sĩ Computer Science AI"
        ),
        # Ứng viên 4: GPA dưới chuẩn tối thiểu (GPA 3.0 < 3.2)
        CandidateProfile(
            candidate_id="CAND-04",
            name="Phạm Văn Dưới Chuẩn (Chưa đạt GPA)",
            target_degree="Thạc sĩ",
            major="Computer Science",
            gpa=3.02,
            ielts=6.0,
            work_exp_years=0.5,
            research_papers=0,
            awards_count=0,
            extracurricular_count=1,
            research_interest="Computer Science"
        )
    ]

    print(f"\n[+] Học bổng mục tiêu: {test_scholarship.title}")
    print(f"    - Yêu cầu sàn: GPA >= {test_scholarship.min_gpa} | IELTS >= {test_scholarship.min_ielts} | Exp >= {test_scholarship.min_work_exp} năm\n")

    results = rank_candidates(test_scholarship, candidates)

    print(f"{'HẠNG':<5} | {'HỌ TÊN ỨNG VIÊN':<35} | {'GPA':<5} | {'IELTS':<6} | {'PAPERS':<7} | {'GIẢI':<5} | {'ĐIỂM HỒ SƠ':<11} | {'MATCH %':<8} | {'TỔNG ĐIỂM':<10} | {'TRẠNG THÁI'}")
    print("-" * 125)

    for rank, r in enumerate(results, start=1):
        status = "ĐẠT CHUẨN" if r["is_eligible"] else f"BỊ LOẠI ({', '.join(r['gaps'])})"
        print(
            f"{rank:<5} | "
            f"{r['name']:<35} | "
            f"{r['gpa']:<5} | "
            f"{r['ielts']:<6} | "
            f"{r['research_papers']:<7} | "
            f"{r['awards_count']:<5} | "
            f"{r['strength_score']:<11} | "
            f"{r['semantic_score']:<8} | "
            f"{r['final_score']:<10} | "
            f"{status}"
        )

    print("\n[✓] KẾT LUẬN: Ứng viên có các chỉ số cao và nhiều thành tích vượt trội (GPA 3.92, IELTS 8.0, 3 Papers, 4 Awards)")
    print("    tự động đạt điểm Profile Strength cao nhất và đứng TOP 1, phân tầng rõ rệt xuống dần theo thứ tự ưu tiên.")
