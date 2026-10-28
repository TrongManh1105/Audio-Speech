-- ============================================================================
-- SCHEMA TRIỂN KHAI VECTOR DATABASE TRÊN POSTGRESQL (PGVECTOR)
-- DÀNH CHO HỆ THỐNG SO KHỚP HỌC BỔNG & HỒ SƠ ỨNG VIÊN
-- ============================================================================

-- 1. Bật extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Bảng dữ liệu học bổng cào về (16 trường chuẩn hóa + Vector Embedding)
DROP TABLE IF EXISTS scholarships CASCADE;
CREATE TABLE scholarships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(500) NOT NULL,
    source_name VARCHAR(100),
    host_country VARCHAR(150),
    degree_level VARCHAR(100),                     -- Cử nhân, Thạc sĩ, Tiến sĩ...
    major_applied TEXT,                            -- Ngành áp dụng (STEM, AI, Kinh tế...)
    funding_type VARCHAR(100),                     -- Toàn phần, Bán phần...
    funding_details TEXT,
    min_gpa NUMERIC(3, 2),                         -- Thang 4.0
    min_ielts NUMERIC(3, 1),                       -- Ngưỡng IELTS
    min_work_exp_years NUMERIC(3, 1) DEFAULT 0,
    age_limit_text VARCHAR(100),
    checklist TEXT,
    commitment TEXT,
    deadline VARCHAR(200),
    apply_method VARCHAR(255),
    link TEXT,
    raw_content TEXT,                              -- Toàn bộ ngữ cảnh để embed
    embedding vector(1536),                        -- Vector 1536 dims (OpenAI text-embedding-3-small) hoặc 768 dims (BGE/BERT)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Bảng hồ sơ ứng viên (Thông tin học thuật, Chỉ số định lượng + Vector Định hướng)
DROP TABLE IF EXISTS candidate_profiles CASCADE;
CREATE TABLE candidate_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    target_degree VARCHAR(100),                    -- Nguyện vọng bậc học
    preferred_country VARCHAR(150),
    major VARCHAR(255),                            -- Chuyên ngành hiện tại
    
    -- === CÁC CHỈ SỐ HỌC THUẬT & NĂNG LỰC CỨNG (GPA, Ngoại ngữ, Kinh nghiệm) ===
    gpa NUMERIC(3, 2) NOT NULL,                    -- Thang 4.0 (VD: 3.85)
    ielts_score NUMERIC(3, 1) DEFAULT 0.0,         -- Điểm IELTS (VD: 8.0)
    topik_level INT DEFAULT 0,                     -- Chứng chỉ tiếng Hàn (nếu có: 1-6)
    work_exp_years NUMERIC(3, 1) DEFAULT 0.0,      -- Số năm kinh nghiệm làm việc
    
    -- === CÁC CHỈ SỐ ĐỊNH LƯỢNG THÀNH TÍCH (CÀNG NHIỀU CÀNG ĐƯỢC ƯU TIÊN CAO) ===
    research_papers_count INT DEFAULT 0,           -- Số lượng bài báo khoa học (Scopus/ISI/Hội nghị)
    awards_count INT DEFAULT 0,                    -- Số lượng giải thưởng học thuật/nghiệp vụ
    extracurricular_count INT DEFAULT 0,           -- Số hoạt động ngoại khóa, tình nguyện quốc tế
    leadership_roles_count INT DEFAULT 0,          -- Số vị trí lãnh đạo (Club Leader, PM...)

    -- === TÓM TẮT ĐỊNH HƯỚNG VÀ VECTOR ĐẶC TRƯNG ===
    profile_summary TEXT,                          -- Đoạn mô tả định hướng nghiên cứu & mục tiêu nghề nghiệp
    embedding vector(1536),                        -- Vector biểu diễn hồ sơ học thuật & định hướng
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- 4. TẠO INDEX HNSW (Hierarchical Navigable Small World) CHO VECTOR SEARCH
-- Tối ưu tốc độ tìm kiếm Cosine Similarity với lượng lớn bản ghi
-- ============================================================================
CREATE INDEX idx_scholarships_embedding 
ON scholarships 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

CREATE INDEX idx_candidate_embedding 
ON candidate_profiles 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Index lọc phụ trợ tăng tốc
CREATE INDEX idx_scholarships_degree ON scholarships (degree_level);
CREATE INDEX idx_scholarships_country ON scholarships (host_country);
CREATE INDEX idx_candidate_gpa ON candidate_profiles (gpa);
CREATE INDEX idx_candidate_ielts ON candidate_profiles (ielts_score);

-- ============================================================================
-- 5. FUNCTION: XẾP HẠNG ỨNG VIÊN CHO MỘT HỌC BỔNG CỤ THỂ
-- Công thức kết hợp: Vector Semantic + Độ lớn các chỉ số (GPA, IELTS, Papers, Awards)
-- Ứng viên có chỉ số cao và nhiều sẽ đứng Top 1 rồi giảm dần
-- ============================================================================
CREATE OR REPLACE FUNCTION rank_candidates_for_scholarship(
    p_scholarship_id UUID,
    p_limit INT DEFAULT 20
)
RETURNS TABLE (
    candidate_id UUID,
    full_name VARCHAR(255),
    gpa NUMERIC(3, 2),
    ielts_score NUMERIC(3, 1),
    research_papers_count INT,
    awards_count INT,
    work_exp_years NUMERIC(3, 1),
    semantic_match_pct NUMERIC(5, 2),      -- Độ tương đồng ngữ nghĩa (%)
    profile_strength_score NUMERIC(5, 2),  -- Điểm đo lường độ khủng & số lượng thành tích
    final_rank_score NUMERIC(5, 2),        -- Điểm tổng hợp xếp hạng (Max: 100)
    eligibility_status TEXT                -- Đạt / Chưa đạt chuẩn tối thiểu
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_sch_vector vector(1536);
    v_min_gpa NUMERIC(3, 2);
    v_min_ielts NUMERIC(3, 1);
    v_min_work NUMERIC(3, 1);
BEGIN
    -- Lấy thông tin học bổng mục tiêu
    SELECT embedding, COALESCE(min_gpa, 3.0), COALESCE(min_ielts, 6.0), COALESCE(min_work_exp_years, 0.0)
    INTO v_sch_vector, v_min_gpa, v_min_ielts, v_min_work
    FROM scholarships
    WHERE id = p_scholarship_id;

    RETURN QUERY
    WITH scored_candidates AS (
        SELECT 
            c.id AS cand_id,
            c.full_name,
            c.gpa,
            c.ielts_score,
            c.research_papers_count,
            c.awards_count,
            c.work_exp_years,
            
            -- 1. Độ tương đồng ngữ nghĩa vector: (1 - Cosine Distance) quy ra thang 0 - 100
            ROUND(((1 - (c.embedding <=> v_sch_vector)) * 100)::numeric, 2) AS sim_score,
            
            -- 2. Điểm sức mạnh chỉ số (Profile Strength Score - Thang 0 - 100):
            --    - GPA (thang 4.0): tỷ trọng 30 điểm
            --    - IELTS (thang 9.0): tỷ trọng 25 điểm
            --    - Kinh nghiệm làm việc: tối đa 15 điểm (bão hòa ở 5 năm)
            --    - Số lượng bài báo nghiên cứu: 15 điểm (3 điểm/bài, tối đa 15)
            --    - Số lượng giải thưởng: 15 điểm (3 điểm/giải, tối đa 15)
            ROUND((
                (LEAST(c.gpa / 4.0, 1.0) * 30.0) +
                (LEAST(GREATEST(c.ielts_score - 4.0, 0) / 5.0, 1.0) * 25.0) +
                (LEAST(c.work_exp_years / 5.0, 1.0) * 15.0) +
                (LEAST(c.research_papers_count * 3.0, 15.0)) +
                (LEAST(c.awards_count * 3.0, 15.0))
            )::numeric, 2) AS strength_score,
            
            -- 3. Kiểm tra điều kiện tối thiểu (Hard Eligibility)
            CASE 
                WHEN c.gpa < v_min_gpa THEN 'THIẾU GPA TỐI THIỂU'
                WHEN c.ielts_score < v_min_ielts THEN 'THIẾU NGOẠI NGỮ'
                WHEN c.work_exp_years < v_min_work THEN 'THIẾU KINH NGHIỆM'
                ELSE 'ĐẠT TIÊU CHUẨN'
            END AS status,

            CASE 
                WHEN c.gpa < v_min_gpa OR c.ielts_score < v_min_ielts OR c.work_exp_years < v_min_work 
                THEN 30.0 -- Phạt điểm nếu không đủ chuẩn tối thiểu
                ELSE 0.0
            END AS penalty
        FROM candidate_profiles c
    )
    SELECT 
        s.cand_id,
        s.full_name,
        s.gpa,
        s.ielts_score,
        s.research_papers_count,
        s.awards_count,
        s.work_exp_years,
        s.sim_score,
        s.strength_score,
        -- Final Ranking: 40% Semantic Match + 60% Strength Score (Chỉ số cao & nhiều) - Penalty
        ROUND((0.40 * s.sim_score + 0.60 * s.strength_score - s.penalty)::numeric, 2) AS final_rank_score,
        s.status
    FROM scored_candidates s
    -- Sắp xếp: Ứng viên chỉ số cao và nhiều + định hướng khớp nhất lên TOP 1
    ORDER BY (0.40 * s.sim_score + 0.60 * s.strength_score - s.penalty) DESC
    LIMIT p_limit;
END;
$$;
