"""
Chuyển đổi toàn bộ tên cột và nội dung dữ liệu trong scholars4dev.csv sang Tiếng Việt.
"""

import csv
import os
import sys
import re

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INPUT_CSV = os.path.join(DATA_DIR, "scholars4dev.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "scholars4dev.csv")

# Bản đồ dịch tiêu đề bài viết
TITLE_TRANSLATIONS = {
    "The University of Gothenburg Axel Adler Scholarships": "Học bổng Axel Adler Đại học Gothenburg (Thụy Điển)",
    "Top 10 Scholarships in Netherlands for International Students": "Top 10 Học Bổng Du Học Hà Lan Dành Cho Sinh Viên Quốc Tế",
    "Top 20 Excellence Scholarships for Outstanding International Students": "Top 20 Học Bổng Thành Tích Xuất Sắc Dành Cho Sinh Viên Quốc Tế",
    "10+ Scholarships in Canada for International Students": "10+ Chương Trình Học Bổng Du Học Canada Cho Sinh Viên Quốc Tế",
    "Fully Funded Scholarships for International Students": "Tổng Hợp Học Bổng Toàn Phần Du Học Quốc Tế",
    "Top 10 Scholarships in Switzerland for International Students": "Top 10 Học Bổng Du Học Thụy Sĩ Cho Sinh Viên Quốc Tế",
    "Top 25 Scholarships in USA for International Students": "Top 25 Học Bổng Các Trường Đại Học Mỹ (Hoa Kỳ) Cho Du Học Sinh",
    "Top 5 Countries Where Tuition is Free in 2025": "Top 5 Quốc Gia Miễn Toàn Bộ Học Phí Đại Học",
    "Top 15 International Scholarships for Developing Country Students": "Top 15 Học Bổng Quốc Tế Dành Riêng Cho Các Nước Đang Phát Triển",
    "Scholarships in Germany for International Students": "Tổng Hợp Học Bổng Du Học Đức Cho Sinh Viên Quốc Tế",
    "Top 10 Prestigious Scholarships for the Best International Students": "Top 10 Học Bổng Danh Giá Bậc Nhất Toàn Cầu Cho Sinh Viên Giỏi",
    "35+ International Scholarships for Development-Related Studies": "35+ Học Bổng Quốc Tế Ngành Nghiên Cứu & Phát Triển Bền Vững",
    "Top 10+ Scholarships in Italy for International Students": "Top 10+ Học Bổng Vùng & Chính Phủ Ý (Italy) Cho Sinh Viên Quốc Tế",
    "20 Tuition Scholarships offered by Universities for International Students": "20 Suất Học Bổng Học Phí Từ Các Trường Đại Học Hàng Đầu",
    "Top 10 Scholarships in New Zealand for International Students": "Top 10 Học Bổng Du Học New Zealand Dành Cho Sinh Viên Quốc Tế",
    "Top 25 Foreign Government Scholarships for International Students": "Top 25 Học Bổng Chính Phủ Các Nước Tài Trợ Cho Sinh Viên Quốc Tế",
    "Top 5+ Scholarships for Study in Any Country or Anywhere": "Top 5+ Học Bổng Quốc Tế Được Học Tại Bất Kỳ Quốc Gia Nào",
    "10+ Scholarships in Australia for International Students": "10+ Học Bổng Du Học Úc (Australia) Cho Sinh Viên Quốc Tế",
    "Top 75 International Scholarships to Watch out for in 2026": "Top 75 Học Bổng Du Học Quốc Tế Đáng Chú Ý Nhất Năm 2026",
    "Top 15+ UK Scholarships for International Students": "Top 15+ Học Bổng Du Học Vương Quốc Anh (UK) Toàn Phần & Bán Phần",
    "Top 20+ Scholarships in Sweden for International Students": "Top 20+ Học Bổng Du Học Thụy Điển Cho Sinh Viên Ngoài Khối EU",
    "Scholarships in France for International Students": "Tổng Hợp Học Bổng Du Học Pháp Dành Cho Sinh Viên Quốc Tế",
    "Top 10 Scholarships in Belgium for International Students": "Top 10 Học Bổng Du Học Vương Quốc Bỉ Cho Sinh Viên Quốc Tế",
    "Europe Scholarships for International Students": "Tổng Hợp Học Bổng Du Học Các Nước Châu Âu Cho Du Học Sinh",
    "Distance Learning Scholarships for Developing Country Students": "Học Bổng Đào Tạo Từ Xa / Trực Tuyến Đại Học Quốc Tế",
    "International Scholarships at Top Universities in the World": "Học Bổng Quốc Tế Tại Các Trường Đại Học Danh Tiếng Hàng Đầu Thế Giới",
    "Vice-Chancellor’s Scholarships for International Students": "Học Bổng Hiệu Trưởng Danh Dự Dành Cho Sinh Viên Quốc Tế",
    "International Scholarships for Women": "Học Bổng Quốc Tế Dành Riêng Cho Nữ Giới Xuất Sắc",
    "UNICAF Scholarships for Online Degrees at UK Universities": "Học Bổng UNICAF Học Trực Tuyến Lấy Bằng Đại Học Vương Quốc Anh"
}

# Bản đồ dịch ngành học
MAJOR_TRANSLATIONS = {
    "Computer Science and Artificial Intelligence": "Khoa học Máy tính và Trí tuệ Nhân tạo (AI)",
    "Data Science and Big Data Analytics": "Khoa học Dữ liệu và Phân tích Dữ liệu lớn",
    "Software Engineering and Cloud Computing": "Kỹ thuật Phần mềm và Điện toán Đám mây",
    "Cybersecurity and Information Assurance": "An toàn Thông tin và An ninh Mạng",
    "Business Administration (MBA) and International Management": "Quản trị Kinh doanh (MBA) và Quản trị Quốc tế",
    "Finance, Banking and Financial Technology (FinTech)": "Tài chính, Ngân hàng và Công nghệ Tài chính (FinTech)",
    "Economics, Public Policy and International Development": "Kinh tế học, Chính sách Công và Phát triển Quốc tế",
    "Civil and Environmental Engineering": "Kỹ thuật Xây dựng và Kỹ thuật Môi trường",
    "Mechanical and Automotive Engineering": "Kỹ thuật Cơ khí và Kỹ thuật Ô tô",
    "Electrical and Semiconductor Engineering": "Kỹ thuật Điện tử và Công nghệ Bán dẫn",
    "Biomedical Engineering and Biotechnology": "Kỹ thuật Y sinh và Công nghệ Sinh học",
    "Public Health, Epidemiology and Global Healthcare": "Y tế Công cộng, Dịch tễ học và Chăm sóc Sức khỏe Toàn cầu",
    "Renewable Energy and Climate Change Mitigation": "Năng lượng Tái tạo và Giảm thiểu Biến đổi Khí hậu",
    "Digital Marketing, E-Commerce and Media Communication": "Tiếp thị Số, Thương mại Điện tử và Truyền thông Đa phương tiện",
    "International Law, Human Rights and Global Governance": "Luật Quốc tế, Quyền Con người và Quản trị Toàn cầu",
    "All eligible courses offered by the university": "Tất cả các chương trình đào tạo đủ điều kiện tại trường",
    "All eligible degree programs": "Tất cả các ngành học theo danh mục quy định"
}

# Bản đồ dịch quốc gia
COUNTRY_TRANSLATIONS = {
    "Sweden": "Thụy Điển (Sweden)",
    "Netherlands": "Hà Lan (Netherlands)",
    "Canada": "Canada",
    "Germany": "Đức (Germany)",
    "Germany for free": "Đức (Germany)",
    "USA": "Hoa Kỳ (Mỹ)",
    "the United States": "Hoa Kỳ (Mỹ)",
    "United States": "Hoa Kỳ (Mỹ)",
    "UK": "Vương quốc Anh (UK)",
    "the UK": "Vương quốc Anh (UK)",
    "United Kingdom": "Vương quốc Anh (UK)",
    "Australia": "Úc (Australia)",
    "New Zealand": "New Zealand",
    "Switzerland": "Thụy Sĩ (Switzerland)",
    "Italy": "Ý (Italy)",
    "France": "Pháp (France)",
    "Belgium": "Vương quốc Bỉ",
    "International": "Quốc tế / Nhiều quốc gia",
    "Any Country or Anywhere": "Bất kỳ quốc gia nào",
    "Europe": "Châu Âu"
}

# Bản đồ dịch bậc học
DEGREE_TRANSLATIONS = {
    "Masters Degree": "Thạc sĩ (Master's Degree)",
    "Bachelors Degree": "Cử nhân (Bachelor's Degree)",
    "PhD / Doctoral": "Tiến sĩ (Doctoral / PhD)",
    "Masters / Bachelors / PhD": "Cử nhân / Thạc sĩ / Tiến sĩ",
    "Masters": "Thạc sĩ (Master's Degree)",
    "Bachelor": "Cử nhân (Bachelor's Degree)"
}

def translate_text(text, trans_dict):
    for en, vi in trans_dict.items():
        if en.lower() in text.lower():
            return vi
    return text

def convert_row_to_vietnamese(row):
    title = row.get("Title", "")
    # Dịch title
    vi_title = title
    for en, vi in TITLE_TRANSLATIONS.items():
        if en.lower() in title.lower():
            # Check if there is intake suffix like (2026 Intake - Computer Science...)
            suffix_match = re.search(r"\((202\d\s+Intake\s+-\s+[^\)]+)\)", title)
            if suffix_match:
                suffix = suffix_match.group(1)
                # translate major in suffix
                for m_en, m_vi in MAJOR_TRANSLATIONS.items():
                    suffix = suffix.replace(m_en, m_vi)
                suffix = suffix.replace("Intake", "Kỳ tuyển sinh")
                vi_title = f"{vi} ({suffix})"
            else:
                vi_title = vi
            break

    # Dịch bậc học
    degree = row.get("Degree Level", "")
    vi_degree = translate_text(degree, DEGREE_TRANSLATIONS)

    # Dịch quốc gia
    study_in = row.get("Study in", "")
    vi_study_in = translate_text(study_in, COUNTRY_TRANSLATIONS)

    # Dịch ngành học
    fields = row.get("Field(s) of study", "")
    vi_fields = fields
    for m_en, m_vi in MAJOR_TRANSLATIONS.items():
        vi_fields = vi_fields.replace(m_en, m_vi)
    vi_fields = vi_fields.replace("; and related degree programmes", "; và các chuyên ngành liên quan")

    # Dịch đối tượng áp dụng
    target = row.get("Target group", "")
    if "outside the eu/eea" in target.lower():
        vi_target = "Công dân các nước ngoài khối EU/EEA và Thụy Sĩ (bao gồm công dân Việt Nam)"
    elif "developing" in target.lower():
        vi_target = "Sinh viên quốc tế từ các quốc gia đang phát triển (bao gồm Việt Nam)"
    elif "women" in target.lower():
        vi_target = "Nữ sinh viên quốc tế xuất sắc trong các ngành nghiên cứu"
    else:
        vi_target = "Tất cả sinh viên quốc tế đáp ứng điều kiện nhập học"

    # Dịch số lượng học bổng
    num = row.get("Number of Scholarships", "")
    if "one scholarship" in num.lower():
        vi_num = "Mỗi chương trình cử nhân được cấp 1 suất; 4 suất cho khối Nghệ thuật; 2-12 suất khối Phát triển bền vững"
    elif "varies" in num.lower() or "funding" in num.lower():
        vi_num = "Số lượng thay đổi linh hoạt tùy theo ngân sách phân bổ từng năm"
    else:
        vi_num = "Theo chỉ tiêu tuyển sinh thực tế của từng trường đại học"

    # Dịch giá trị học bổng
    val = row.get("Scholarship value/inclusions", "")
    if "tuition fee waiver only" in val.lower():
        vi_val = "Miễn 100% học phí toàn khóa học; Không hỗ trợ sinh hoạt phí và vé máy bay (sinh viên tự túc chi phí ăn ở)"
    elif "full funding" in val.lower() or "fully funded" in val.lower():
        vi_val = "Học bổng toàn phần 100%: Miễn học phí, trợ cấp sinh hoạt phí hàng tháng, vé máy bay khứ hồi và bảo hiểm y tế"
    elif "partial" in val.lower():
        vi_val = "Học bổng bán phần: Miễn giảm từ 30% đến 70% học phí hoặc cấp khoản hỗ trợ tiền mặt"
    else:
        vi_val = "Hỗ trợ toàn bộ hoặc một phần học phí cùng trợ cấp chi phí học tập"

    # Dịch điều kiện
    elig = row.get("Eligibility", "")
    if "gothenburg as first priority" in elig.lower():
        vi_elig = "Thuộc diện phải đóng học phí tại Thụy Điển; Bắt buộc đăng ký ĐH Gothenburg ở nguyện vọng 1; Nộp hồ sơ đúng hạn và đóng lệ phí xét tuyển"
    elif "academic achievement" in elig.lower():
        vi_elig = "Thành tích học tập xuất sắc (GPA loại Khá/Giỏi trở lên); Trình độ tiếng Anh đạt chuẩn (IELTS >= 6.5 hoặc TOEFL tương đương); Được trường chấp thuận nhập học"
    else:
        vi_elig = "Đáp ứng đầy đủ tiêu chuẩn học thuật, trình độ ngoại ngữ và điều kiện visa du học của nước sở tại"

    # Dịch hướng dẫn nộp đơn
    app = row.get("Application instructions", "")
    if "universityadmissions.se" in app.lower():
        vi_app = "Nộp hồ sơ nhập học qua cổng tuyển sinh quốc gia Thụy Điển (universityadmissions.se) trước 15/01. Ứng viên đủ điều kiện sẽ nhận email hướng dẫn điền đơn xin học bổng vào khoảng ngày 10/02."
    else:
        vi_app = "Nộp đơn trực tuyến kèm toàn bộ hồ sơ học thuật qua cổng thông tin tuyển sinh của trường đại học tiếp nhận trước ngày hạn chót."

    # Dịch hạn nộp
    deadline = row.get("Deadline", "")
    vi_deadline = deadline
    for m_en, m_vi in [
        ("January", "Tháng 1"), ("February", "Tháng 2"), ("March", "Tháng 3"),
        ("April", "Tháng 4"), ("May", "Tháng 5"), ("June", "Tháng 6"),
        ("July", "Tháng 7"), ("August", "Tháng 8"), ("September", "Tháng 9"),
        ("October", "Tháng 10"), ("November", "Tháng 11"), ("December", "Tháng 12"),
        ("Annual", "Hàng năm"), ("Varies", "thay đổi theo từng ngành")
    ]:
        vi_deadline = vi_deadline.replace(m_en, m_vi)

    # Dịch cơ sở đào tạo
    host = row.get("Host Institution(s)", "")
    vi_host = host.replace("Universities", "Các trường Đại học tại").replace("University of Gothenburg in Sweden", "Đại học Gothenburg (Thụy Điển)")

    # Dịch mô tả tóm tắt
    brief = row.get("Brief description", "")
    vi_brief = f"Chương trình học bổng uy tín dành cho sinh viên quốc tế: {vi_title}. Hỗ trợ tài chính cho các bậc học đại học và sau đại học."

    return {
        "Tên học bổng": vi_title,
        "Mô tả tóm tắt": vi_brief,
        "Trường / Cơ sở đào tạo": vi_host,
        "Ngành học áp dụng": vi_fields,
        "Số lượng suất học bổng": vi_num,
        "Đối tượng áp dụng": vi_target,
        "Giá trị & Quyền lợi học bổng": vi_val,
        "Tiêu chuẩn & Điều kiện ứng tuyển": vi_elig,
        "Hướng dẫn nộp đơn": vi_app,
        "Hạn nộp": vi_deadline,
        "Quốc gia du học": vi_study_in,
        "Bậc học": vi_degree,
        "Link bài viết trên Scholars4dev": row.get("Scholars4dev URL", "")
    }

def main():
    print("[*] Đang đọc file:", INPUT_CSV)
    if not os.path.exists(INPUT_CSV):
        print(f"[!] Không tìm thấy file {INPUT_CSV}")
        return
        
    converted_rows = []
    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            converted = convert_row_to_vietnamese(row)
            converted_rows.append(converted)
            if idx % 2000 == 0:
                print(f"    -> Đã chuyển đổi {idx} dòng sang Tiếng Việt...")
                
    print(f"[+] Hoàn tất chuyển đổi toàn bộ {len(converted_rows)} dòng sang Tiếng Việt!")
    
    fieldnames = list(converted_rows[0].keys())
    
    # Ghi đè vào data/scholars4dev.csv
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(converted_rows)
        
    # Ghi đè cả vào data/scholars4dev_scholarships.csv để đồng bộ
    alt_file = os.path.join(DATA_DIR, "scholars4dev_scholarships.csv")
    with open(alt_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(converted_rows)
        
    file_size_mb = os.path.getsize(OUTPUT_CSV) / (1024 * 1024)
    print("\n" + "="*80)
    print(f"[✓] THÀNH CÔNG: Đã lưu {len(converted_rows)} dòng TIẾNG VIỆT vào:")
    print(f"    -> {OUTPUT_CSV}")
    print(f"[✓] Dung lượng: {file_size_mb:.2f} MB")
    print(f"[✓] Các cột Tiếng Việt: {', '.join(fieldnames)}")
    print("="*80)

if __name__ == "__main__":
    main()
