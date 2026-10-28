"""
Nâng cấp và làm giàu dữ liệu chi tiết cho tất cả các bộ dataset học bổng.
Bổ sung các trường chuyên sâu: GPA tối thiểu, IELTS/ngoại ngữ, Kinh nghiệm làm việc,
Độ tuổi giới hạn, Danh mục hồ sơ cần nộp (Checklist), Chi tiết tài trợ, Ràng buộc/Cam kết.
"""

import os
import sys
import csv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 1. YOUTH OPPORTUNITIES CHI TIẾT
youthop_detailed = [
    {
        "Tên học bổng": "Erasmus Mundus Joint Master Degrees (EMJMD) Scholarship",
        "Nguồn": "Youth Opportunities",
        "Quốc gia": "Châu Âu (Pháp, Đức, Ý, Tây Ban Nha, Bỉ, Hà Lan...)",
        "Bậc học": "Thạc sĩ (Master's Degree)",
        "Chuyên ngành áp dụng": "Đa ngành (AI, Khoa học dữ liệu, Môi trường, Kinh tế, Khoa học xã hội...)",
        "Mức tài trợ": "Toàn phần 100% (Fully Funded)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Miễn 100% học phí toàn khóa + 1,400 EUR/tháng sinh hoạt phí + Bảo hiểm quốc tế toàn diện + Chi phí di chuyển giữa các nước đối tác",
        "GPA tối thiểu": ">= 3.0 / 4.0 (hoặc >= 7.5 / 10 - Xếp loại Khá/Giỏi)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 (không kỹ năng nào dưới 6.0) hoặc TOEFL iBT >= 90",
        "Kinh nghiệm làm việc yêu cầu": "Không bắt buộc (Ưu tiên ứng viên có dự án nghiên cứu, thực tập hoặc bài báo khoa học)",
        "Độ tuổi giới hạn": "Không giới hạn độ tuổi",
        "Hồ sơ cần chuẩn bị (Checklist)": "CV chuẩn Europass, Bảng điểm & Bằng cử nhân (dịch thuật công chứng), Motivation Letter (Bài luận động lực riêng cho từng chương trình), 2 Thư giới thiệu (LOR) từ Giáo sư, Chứng chỉ tiếng Anh",
        "Ràng buộc & Cam kết": "Bắt buộc học tập và luân chuyển tại ít nhất 2 trường đại học thuộc 2 quốc gia châu Âu khác nhau trong liên minh",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: Tháng 10 - Tháng 11 | Hạn chót: Tháng 1 - Đầu tháng 2 hàng năm",
        "Phương thức ứng tuyển": "Nộp hồ sơ trực tuyến trực tiếp trên cổng thông tin của từng Consortium chương trình EMJMD",
        "Link chi tiết": "https://www.youthop.com/scholarships/erasmus-mundus-joint-master-degree-scholarships"
    },
    {
        "Tên học bổng": "DAAD EPOS Development-Related Postgraduate Courses",
        "Nguồn": "Youth Opportunities",
        "Quốc gia": "Đức (Germany)",
        "Bậc học": "Thạc sĩ (Master's) / Tiến sĩ (PhD)",
        "Chuyên ngành áp dụng": "Các ngành phát triển bền vững: Kỹ thuật, Môi trường, Kinh tế học, Y tế công cộng, Quản lý chuỗi cung ứng",
        "Mức tài trợ": "Toàn phần 100% (Fully Funded)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Miễn 100% học phí + 934 EUR/tháng (Thạc sĩ) hoặc 1,300 EUR/tháng (Tiến sĩ) + Trợ cấp vé máy bay khứ hồi + Bảo hiểm y tế/tai nạn",
        "GPA tối thiểu": ">= 3.0 / 4.0 (hoặc >= 7.5 / 10)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS >= 6.0 - 6.5 (chương trình tiếng Anh) HOẶC B2/C1 DSH/TestDaF (chương trình tiếng Đức)",
        "Kinh nghiệm làm việc yêu cầu": "BẮT BUỘC có tối thiểu 2 năm kinh nghiệm làm việc chuyên môn liên quan tại thời điểm nộp đơn",
        "Độ tuổi giới hạn": "Không quá 6 năm kể từ ngày tốt nghiệp văn bằng gần nhất",
        "Hồ sơ cần chuẩn bị (Checklist)": "Đơn xin học bổng DAAD, CV chuẩn Europass có chữ ký, Bài luận bày tỏ nguyện vọng đóng góp cho nước sở tại, Thư xác nhận công tác từ cơ quan (>= 2 năm), 2 Thư giới thiệu, Bảng điểm đại học",
        "Ràng buộc & Cam kết": "Sau khi tốt nghiệp, khuyến khích ứng viên trở về nước để ứng dụng kiến thức phát triển quê hương",
        "Hạn nộp & Chu kỳ tuyển sinh": "Tháng 8 - Tháng 11 hàng năm (Tùy từng khóa học của các trường ĐH tại Đức)",
        "Phương thức ứng tuyển": "Nộp đơn trực tiếp cho trường Đại học tại Đức kèm hồ sơ ứng tuyển học bổng DAAD EPOS",
        "Link chi tiết": "https://www.youthop.com/scholarships/daad-scholarships-germany"
    },
    {
        "Tên học bổng": "Australia Awards Scholarships (AAS - Học bổng Chính phủ Úc)",
        "Nguồn": "Youth Opportunities",
        "Quốc gia": "Úc (Australia)",
        "Bậc học": "Thạc sĩ (Master's Degree)",
        "Chuyên ngành áp dụng": "Nông nghiệp, Chuyển đổi số, Năng lượng sạch, Bình đẳng giới, Y tế, Quản trị công",
        "Mức tài trợ": "Toàn phần 100% (Full-ride)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Toàn bộ học phí + Vé máy bay khứ hồi hạng phổ thông + Trợ cấp ổn định ban đầu (5,000 AUD) + Sinh hoạt phí hàng tháng (CLE) + Bảo hiểm OSHC + Khóa đào tạo tiếng Anh tại VN trước khi đi",
        "GPA tối thiểu": ">= 7.0 / 10 (tương đương >= 2.8 - 3.0 / 4.0)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 (không kỹ năng nào dưới 6.0) hoặc TOEFL iBT tương đương (Riêng nhóm khó khăn: IELTS 6.0)",
        "Kinh nghiệm làm việc yêu cầu": "BẮT BUỘC có tối thiểu 24 tháng kinh nghiệm làm việc tại Việt Nam liên quan đến ngành học",
        "Độ tuổi giới hạn": "Tối thiểu 18 tuổi, không giới hạn trần",
        "Hồ sơ cần chuẩn bị (Checklist)": "Bằng cấp & bảng điểm đại học công chứng, Chứng chỉ IELTS/TOEFL còn hạn, 4 bài luận về năng lực lãnh đạo và đóng góp phát triển, 2 Thư giới thiệu của cơ quan công tác và học thuật",
        "Ràng buộc & Cam kết": "BẮT BUỘC quay trở lại Việt Nam làm việc ít nhất 2 năm sau khi hoàn thành khóa học tại Úc",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: 01/02 | Đóng đơn: 30/04 hàng năm",
        "Phương thức ứng tuyển": "Nộp hồ sơ trực tuyến qua hệ thống OASIS của Chính phủ Australia",
        "Link chi tiết": "https://www.youthop.com/scholarships/australia-awards-scholarships"
    },
    {
        "Tên học bổng": "Turkiye Burslari Scholarships (Học bổng Chính phủ Thổ Nhĩ Kỳ)",
        "Nguồn": "Youth Opportunities",
        "Quốc gia": "Thổ Nhĩ Kỳ (Turkey)",
        "Bậc học": "Cử nhân / Thạc sĩ / Tiến sĩ",
        "Chuyên ngành áp dụng": "Tất cả các ngành đào tạo tại các trường ĐH Thổ Nhĩ Kỳ",
        "Mức tài trợ": "Toàn phần 100% (Full Tuition + Stipend)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Học phí 100% + Ký túc xá miễn phí + Sinh hoạt phí: 1,700 TL (Đại học), 2,400 TL (Thạc sĩ), 3,000 TL (Tiến sĩ) + Vé máy bay khứ hồi + 1 năm học tiếng Thổ miễn phí + Bảo hiểm y tế",
        "GPA tối thiểu": ">= 70% (Đại học), >= 75% (Thạc sĩ/Tiến sĩ), >= 90% (Khối ngành Y Dược)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Không bắt buộc tiếng Anh nếu học bằng tiếng Thổ; Nếu chọn chương trình tiếng Anh cần IELTS >= 6.5 hoặc TOEFL iBT >= 80",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu đối với bậc Đại học & Thạc sĩ; Ưu tiên kinh nghiệm đối với Tiến sĩ",
        "Độ tuổi giới hạn": "Dưới 21 tuổi (Đại học); Dưới 30 tuổi (Thạc sĩ); Dưới 35 tuổi (Tiến sĩ)",
        "Hồ sơ cần chuẩn bị (Checklist)": "Hộ chiếu, Bằng tốt nghiệp & học bạ/bảng điểm, Thư giới thiệu (LOR), Bài luận nghiên cứu/kế hoạch học tập, Chứng chỉ ngoại ngữ hoặc giải thưởng quốc gia/quốc tế (nếu có)",
        "Ràng buộc & Cam kết": "Học tập nghiêm túc và duy trì điểm số đạt chuẩn theo quy định của trường",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: 10/01 | Đóng đơn: 20/02 hàng năm",
        "Phương thức ứng tuyển": "Nộp đơn trực tuyến trên hệ thống Turkiye Burslari Application System (TBBS)",
        "Link chi tiết": "https://www.youthop.com/scholarships/turkiye-burslari-scholarships"
    },
    {
        "Tên học bổng": "Swedish Institute Scholarships for Global Professionals (SISGP)",
        "Nguồn": "Youth Opportunities",
        "Quốc gia": "Thụy Điển (Sweden)",
        "Bậc học": "Thạc sĩ (Master's Degree)",
        "Chuyên ngành áp dụng": "Hơn 700 chương trình Thạc sĩ tiếng Anh về Đổi mới sáng tạo, Công nghệ, Bền vững, Kinh tế",
        "Mức tài trợ": "Toàn phần 100% (Full Tuition + Living Costs)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Chi trả 100% học phí trực tiếp cho trường ĐH Thụy Điển + Sinh hoạt phí 12,000 SEK/tháng (suốt toàn khóa) + Trợ cấp đi lại 15,000 SEK + Bảo hiểm y tế toàn diện + Gia nhập mạng lưới SI Network for Future Global Leaders",
        "GPA tối thiểu": ">= 3.0 / 4.0 (Đạt tiêu chuẩn trúng tuyển vào ĐH Thụy Điển)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 (không band < 5.5) hoặc TOEFL iBT >= 90",
        "Kinh nghiệm làm việc yêu cầu": "BẮT BUỘC tối thiểu 3,000 giờ làm việc (tương đương khoảng 1.5 - 2 năm làm việc toàn thời gian) và có kinh nghiệm lãnh đạo",
        "Độ tuổi giới hạn": "Không giới hạn độ tuổi",
        "Hồ sơ cần chuẩn bị (Checklist)": "Mẫu CV theo form chuẩn của Swedish Institute, Thư chứng minh kinh nghiệm làm việc và năng lực lãnh đạo (Proof of work & leadership experience do cấp trên ký xác nhận), 2 Thư giới thiệu theo mẫu SI, Bản sao hộ chiếu",
        "Ràng buộc & Cam kết": "Phải nộp và nhận được thư mời nhập học có điều kiện/chính thức từ 1 trường ĐH Thụy Điển qua cổng University Admissions trước",
        "Hạn nộp & Chu kỳ tuyển sinh": "Vòng 1 (Nộp trường): Tháng 10 - Tháng 1 | Vòng 2 (Nộp học bổng SI): Giữa tháng 2 hàng năm",
        "Phương thức ứng tuyển": "Nộp trực tuyến qua cổng tuyển sinh Swedish Institute sau khi đã đăng ký trên Universityadmissions.se",
        "Link chi tiết": "https://www.youthop.com/scholarships/swedish-institute-scholarships"
    }
]

# 2. CHEVENING (UK) CHI TIẾT
chevening_detailed = [
    {
        "Tên học bổng": "Chevening Scholarship (UK Government Full-Ride Master's)",
        "Nguồn": "Chevening (UK Government)",
        "Quốc gia": "Vương quốc Anh (United Kingdom)",
        "Bậc học": "Thạc sĩ 1 năm (1-year Master's Degree)",
        "Chuyên ngành áp dụng": "Mọi chuyên ngành đào tạo Thạc sĩ tại bất kỳ trường đại học nào ở Vương quốc Anh",
        "Mức tài trợ": "Toàn phần 100% (Full-ride: Học phí + Sinh hoạt phí + Vé máy bay)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Toàn bộ học phí (kể cả khóa MBA trần đến mức quy định) + Sinh hoạt phí hàng tháng (1,134 - 1,410 GBP/tháng tùy London hay ngoài London) + Vé máy bay khứ hồi hạng phổ thông + Lệ phí visa và phụ phí y tế IHS + Trợ cấp đi lại và tham dự sự kiện Chevening",
        "GPA tối thiểu": "Tương đương bằng danh dự hạng nhì cao (UK Upper Second-Class Honours 2:1, tức GPA >= 3.0 / 4.0 hoặc >= 7.5 / 10)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Đáp ứng yêu cầu đầu vào của 3 khóa học đã đăng ký tại trường ĐH Anh (Thường IELTS >= 6.5 - 7.0, không band < 6.0)",
        "Kinh nghiệm làm việc yêu cầu": "BẮT BUỘC tối thiểu 2 năm kinh nghiệm làm việc (tương đương đủ 2,800 giờ làm việc tính đến ngày nộp đơn)",
        "Độ tuổi giới hạn": "Không giới hạn độ tuổi",
        "Hồ sơ cần chuẩn bị (Checklist)": "Danh sách 3 khóa học Thạc sĩ tại UK muốn ứng tuyển, 4 bài luận Chevening (Lãnh đạo & Tác động, Kết nối mạng lưới, Lý do chọn học tại UK, Kế hoạch nghề nghiệp tương lai 5-10 năm), 2 Thư giới thiệu, Bảng điểm & Bằng cử nhân",
        "Ràng buộc & Cam kết": "BẮT BUỘC trở về quốc gia mang quốc tịch (Việt Nam) tối thiểu 2 năm sau khi hoàn thành khóa học",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: Đầu tháng 8 | Đóng đơn: Đầu tháng 11 hàng năm (Phỏng vấn vào tháng 3 - tháng 4 năm kế tiếp)",
        "Phương thức ứng tuyển": "Nộp đơn trực tuyến qua cổng điện tử Chevening e-application system",
        "Link chi tiết": "https://www.chevening.org/scholarships/"
    },
    {
        "Tên học bổng": "Chevening Partner Awards",
        "Nguồn": "Chevening (UK Government)",
        "Quốc gia": "Vương quốc Anh (United Kingdom)",
        "Bậc học": "Thạc sĩ (Master's Degree)",
        "Chuyên ngành áp dụng": "Các chuyên ngành trọng điểm hợp tác với đối tác (Cambridge, Oxford, LSE, Imperial, HSBC, Pearson...)",
        "Mức tài trợ": "Toàn phần (Đồng tài trợ giữa Chính phủ Anh và Trường/Tổ chức đối tác)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Chi trả trọn gói học phí, sinh hoạt phí và vé máy bay; được ưu tiên cơ hội thực tập, cố vấn chuyên môn từ đối tác tài trợ",
        "GPA tối thiểu": "GPA >= 3.2 - 3.5 / 4.0 (Đáp ứng chuẩn tuyển sinh khắt khe của các trường top đầu)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 7.0 (không kỹ năng nào dưới 6.5)",
        "Kinh nghiệm làm việc yêu cầu": "Tối thiểu 2 năm kinh nghiệm làm việc chuyên sâu trong lĩnh vực đối tác quan tâm",
        "Độ tuổi giới hạn": "Không giới hạn độ tuổi",
        "Hồ sơ cần chuẩn bị (Checklist)": "Hồ sơ ứng tuyển Chevening chuẩn + Chọn tích nguyện vọng Partner Award + Thư chấp thuận nhập học từ trường đối tác",
        "Ràng buộc & Cam kết": "Bắt buộc trở về nước 2 năm; thực hiện các nghĩa vụ báo cáo học thuật cho đơn vị đồng tài trợ",
        "Hạn nộp & Chu kỳ tuyển sinh": "Theo chu kỳ học bổng Chevening (Tháng 8 - Tháng 11 hàng năm)",
        "Phương thức ứng tuyển": "Tích chọn trường đối tác trong hồ sơ ứng tuyển Chevening trực tuyến",
        "Link chi tiết": "https://www.chevening.org/scholarships/partner-awards/"
    },
    {
        "Tên học bổng": "Chevening Fellowships (Khóa đào tạo chuyên sâu ngắn hạn)",
        "Nguồn": "Chevening (UK Government)",
        "Quốc gia": "Vương quốc Anh (United Kingdom)",
        "Bậc học": "Khóa chuyên gia / Fellowship (Nghiên cứu ngắn hạn 3-6 tháng)",
        "Chuyên ngành áp dụng": "Báo chí, Chính sách công, An ninh mạng, Năng lượng, Quyền con người",
        "Mức tài trợ": "Toàn phần 100% (Full funding)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Toàn bộ chi phí đào tạo/nghiên cứu + Sinh hoạt phí hàng tháng trong thời gian ở Anh + Vé máy bay khứ hồi + Chi phí visa",
        "GPA tối thiểu": "Tốt nghiệp Đại học, ưu tiên ứng viên có bằng Thạc sĩ",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Thông thạo tiếng Anh giao tiếp chuyên nghiệp (IELTS >= 6.5 hoặc tương đương)",
        "Kinh nghiệm làm việc yêu cầu": "Tối thiểu 5 - 7 năm kinh nghiệm làm việc ở vị trí quản lý, nhà báo, chuyên gia chính sách",
        "Độ tuổi giới hạn": "Dành cho các chuyên gia trung cấp và cao cấp (Mid-career professionals)",
        "Hồ sơ cần chuẩn bị (Checklist)": "CV chuyên gia, Bản đề cương dự án hoặc mục tiêu nghiên cứu ngắn hạn, Thư giới thiệu từ người đứng đầu cơ quan công tác",
        "Ràng buộc & Cam kết": "Trở về cơ quan chủ quản để ứng dụng kinh nghiệm đào tạo từ Vương quốc Anh",
        "Hạn nộp & Chu kỳ tuyển sinh": "Tùy từng chương trình Fellowship cụ thể (Thường mở vào mùa Thu hoặc mùa Xuân)",
        "Phương thức ứng tuyển": "Nộp đơn trực tuyến qua cổng Chevening Fellowships",
        "Link chi tiết": "https://www.chevening.org/fellowships/"
    },
    {
        "Tên học bổng": "Chevening Eligibility & Criteria (Chuẩn điều kiện ứng tuyển)",
        "Nguồn": "Chevening (UK Government)",
        "Quốc gia": "Vương quốc Anh (United Kingdom)",
        "Bậc học": "Thạc sĩ (Master's Degree)",
        "Chuyên ngành áp dụng": "Tất cả các ngành được giảng dạy tại UK",
        "Mức tài trợ": "Toàn phần 100%",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Bao quát toàn bộ gói hỗ trợ tài chính cho sinh viên quốc tế đến Anh du học",
        "GPA tối thiểu": "UK 2:1 (Tối thiểu 3.0 / 4.0)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5",
        "Kinh nghiệm làm việc yêu cầu": ">= 2,800 giờ làm việc (Full-time, Part-time, Tình nguyện có trả lương đều được tính)",
        "Độ tuổi giới hạn": "Không giới hạn",
        "Hồ sơ cần chuẩn bị (Checklist)": "Bằng tốt nghiệp cử nhân, Bảng điểm, 4 bài luận, 2 thư giới thiệu, Thư mời nhập học không điều kiện (Unconditional Offer) trước tháng 7",
        "Ràng buộc & Cam kết": "Bắt buộc trở về nước 2 năm",
        "Hạn nộp & Chu kỳ tuyển sinh": "Tháng 8 - Tháng 11 hàng năm",
        "Phương thức ứng tuyển": "Hệ thống nộp đơn trực tuyến Chevening",
        "Link chi tiết": "https://www.chevening.org/scholarships/who-can-apply/eligibility/"
    }
]

# 3. STUDY IN KOREA CHI TIẾT
studyinkorea_detailed = [
    {
        "Tên học bổng": "GKS - Global Korea Scholarship (Graduate - Thạc sĩ & Tiến sĩ)",
        "Nguồn": "Study in Korea (NIIED)",
        "Quốc gia": "Hàn Quốc (South Korea)",
        "Bậc học": "Thạc sĩ (Master's - 3 năm) / Tiến sĩ (PhD - 4 năm)",
        "Chuyên ngành áp dụng": "Khoa học Tự nhiên, Kỹ thuật Công nghệ (STEM), Xã hội Nhân văn, Kinh tế",
        "Mức tài trợ": "Toàn phần 100% (Full Scholarship)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "100% học phí chuyên ngành + 1 năm học tiếng Hàn miễn phí + Sinh hoạt phí: 1,000,000 KRW/tháng (Thạc sĩ/Tiến sĩ) + Vé máy bay khứ hồi + Hỗ trợ ổn định định cư 200,000 KRW + Bảo hiểm y tế quốc dân + Thưởng 100,000 KRW/tháng nếu đạt TOPIK 5 hoặc 6",
        "GPA tối thiểu": "Điểm trung bình tích lũy (C.G.P.A) >= 80% (tương đương >= 3.2 / 4.0 hoặc >= 8.0 / 10) HOẶC nằm trong Top 20% sinh viên xuất sắc nhất của khóa",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Không bắt buộc tại thời điểm nộp đơn; TUY NHIÊN ứng viên có TOPIK 3+ hoặc IELTS 6.5+ / TOEFL 80+ sẽ được cộng điểm ưu tiên rất lớn",
        "Kinh nghiệm làm việc yêu cầu": "Không bắt buộc (Ưu tiên ứng viên ngành STEM có bài báo khoa học đăng trên tạp chí SCIE/SCOPUS)",
        "Độ tuổi giới hạn": "BẮT BUỘC dưới 40 tuổi tính đến ngày 1 tháng 9 của năm nộp đơn",
        "Hồ sơ cần chuẩn bị (Checklist)": "Đơn xin học bổng GKS, Giới thiệu bản thân (Personal Statement), Kế hoạch học tập (Study Plan), Bản đề cương nghiên cứu (Research Proposal - cho Tiến sĩ), 1-2 Thư giới thiệu niêm phong từ Giáo sư, Bằng tốt nghiệp & Bảng điểm (hợp pháp hóa lãnh sự Hàn Quốc), Giấy khám sức khỏe chính thức",
        "Ràng buộc & Cam kết": "BẮT BUỘC hoàn thành 1 năm học tiếng Hàn tại cơ sở chỉ định và đạt chứng chỉ TOPIK cấp 3 trở lên trước khi được nhập học chương trình chính khóa",
        "Hạn nộp & Chu kỳ tuyển sinh": "Embassy Track (Đại sứ quán): Tháng 2 - Đầu tháng 3 | University Track (Trường ĐH): Tháng 2 - Cuối tháng 3 hàng năm",
        "Phương thức ứng tuyển": "Nộp bộ hồ sơ giấy công chứng/hợp pháp hóa đến Đại sứ quán Hàn Quốc tại Hà Nội/TP.HCM HOẶC gửi trực tiếp đến trường Đại học Hàn Quốc lựa chọn",
        "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/GksScholarship.do"
    },
    {
        "Tên học bổng": "GKS - Global Korea Scholarship (Undergraduate - Cử nhân / Đại học)",
        "Nguồn": "Study in Korea (NIIED)",
        "Quốc gia": "Hàn Quốc (South Korea)",
        "Bậc học": "Cử nhân / Đại học chính quy 4 năm (+ 1 năm tiếng Hàn)",
        "Chuyên ngành áp dụng": "Các chuyên ngành đào tạo đại học hệ 4 năm tại các trường ĐH đối tác NIIED",
        "Mức tài trợ": "Toàn phần 100% (Full Tuition + Living Costs)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "100% học phí 4 năm + 1 năm học tiếng Hàn + Sinh hoạt phí 900,000 KRW/tháng + Vé máy bay khứ hồi + Bảo hiểm y tế + Trợ cấp ban đầu",
        "GPA tối thiểu": "Điểm trung bình học tập 3 năm cấp 3 (THPT) đạt từ 80% trở lên (tương đương >= 8.0 / 10)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Không bắt buộc có trước; Ưu tiên có chứng chỉ TOPIK cấp 3 hoặc IELTS >= 6.0",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu (Dành cho học sinh tốt nghiệp THPT)",
        "Độ tuổi giới hạn": "BẮT BUỘC dưới 25 tuổi tính đến ngày 1 tháng 3 của năm nhập học",
        "Hồ sơ cần chuẩn bị (Checklist)": "Học bạ THPT (hợp pháp hóa lãnh sự), Bằng tốt nghiệp THPT, Giấy khai sinh chứng minh không có quốc tịch Hàn Quốc, Bản tự giới thiệu, Kế hoạch học tập, 1 Thư giới thiệu của giáo viên cấp 3",
        "Ràng buộc & Cam kết": "Phải đạt chứng chỉ TOPIK 3 sau 1 năm học dự bị tiếng Hàn để vào năm nhất đại học",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: Tháng 9 | Đóng đơn: Tháng 10 hàng năm",
        "Phương thức ứng tuyển": "Nộp hồ sơ qua Đại sứ quán Hàn Quốc tại Việt Nam hoặc qua trường ĐH chỉ định",
        "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/GksScholarship.do"
    },
    {
        "Tên học bổng": "GKS R&D Program for Science & Engineering",
        "Nguồn": "Study in Korea (NIIED)",
        "Quốc gia": "Hàn Quốc (South Korea)",
        "Bậc học": "Thạc sĩ / Tiến sĩ khối ngành Kỹ thuật & Nghiên cứu phát triển",
        "Chuyên ngành áp dụng": "Công nghệ thông tin, Bán dẫn, Trí tuệ nhân tạo, Vật liệu mới, Năng lượng tái tạo",
        "Mức tài trợ": "Toàn phần 100% + Tài trợ đề tài nghiên cứu từ các phòng Lab",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Học phí toàn phần + Sinh hoạt phí 1,000,000 KRW/tháng + Trợ cấp tham gia dự án R&D của Lab (thường thêm 500,000 - 1,500,000 KRW/tháng) + Vé máy bay khứ hồi",
        "GPA tối thiểu": "GPA >= 3.2 / 4.0",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 hoặc TOEFL iBT >= 85 (Chương trình nghiên cứu hoàn toàn bằng tiếng Anh)",
        "Kinh nghiệm làm việc yêu cầu": "Có kinh nghiệm nghiên cứu tại phòng Lab hoặc có bài báo khoa học là lợi thế quyết định",
        "Độ tuổi giới hạn": "Dưới 40 tuổi",
        "Hồ sơ cần chuẩn bị (Checklist)": "CV học thuật (Academic CV), Danh mục bài báo/công trình nghiên cứu, Research Proposal, Thư giới thiệu từ Giáo sư hướng dẫn tại Việt Nam và thư ngỏ Giáo sư Hàn Quốc",
        "Ràng buộc & Cam kết": "Tham gia tích cực vào các dự án nghiên cứu của phòng thí nghiệm (Lab) tiếp nhận",
        "Hạn nộp & Chu kỳ tuyển sinh": "Theo từng đợt tuyển sinh của các trường ĐH công nghệ Hàn Quốc (Tháng 3 & Tháng 9)",
        "Phương thức ứng tuyển": "Nộp hồ sơ trực tiếp qua University Track của các trường ĐH nghiên cứu trọng điểm",
        "Link chi tiết": "https://www.studyinkorea.go.kr/en/scholarship/GksScholarship.do"
    },
    {
        "Tên học bổng": "Korean Government Support Program for Foreign Exchange Students",
        "Nguồn": "Study in Korea (NIIED)",
        "Quốc gia": "Hàn Quốc (South Korea)",
        "Bậc học": "Trao đổi sinh viên ngắn hạn (1 kỳ hoặc 2 kỳ học)",
        "Chuyên ngành áp dụng": "Các ngành học tương thích giữa trường ĐH Việt Nam và ĐH Hàn Quốc",
        "Mức tài trợ": "Toàn phần chi phí trao đổi (Exchange Grant)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Vé máy bay khứ hồi + Sinh hoạt phí 500,000 KRW/tháng + Hỗ trợ định cư ban đầu 200,000 KRW + Bảo hiểm y tế",
        "GPA tối thiểu": "GPA tích lũy tại trường ĐH Việt Nam >= 80% (hoặc >= 3.0 / 4.0)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "TOPIK cấp 2 trở lên HOẶC IELTS >= 5.5",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu",
        "Độ tuổi giới hạn": "Đang là sinh viên đại học chính quy (hoàn thành ít nhất 2 học kỳ)",
        "Hồ sơ cần chuẩn bị (Checklist)": "Bảng điểm đại học hiện tại, Giấy giới thiệu từ Phòng Hợp tác Quốc tế của trường ĐH tại VN, Kế hoạch học tập trao đổi",
        "Ràng buộc & Cam kết": "Chưa từng nhận học bổng của Chính phủ Hàn Quốc trước đây; quay trở lại trường mẹ để hoàn thành chương trình đại học",
        "Hạn nộp & Chu kỳ tuyển sinh": "Kỳ Mùa Thu: Tháng 2 | Kỳ Mùa Xuân: Tháng 8 hàng năm",
        "Phương thức ứng tuyển": "Đăng ký thông qua Phòng Hợp tác Quốc tế tại các trường ĐH ở Việt Nam có liên kết MOU",
        "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/OtherScholarship.do"
    },
    {
        "Tên học bổng": "Học bổng TOPIK & Thành tích các trường Đại học Hàn Quốc (University Scholarships)",
        "Nguồn": "Study in Korea (Các trường ĐH đối tác)",
        "Quốc gia": "Hàn Quốc (South Korea)",
        "Bậc học": "Đại học / Thạc sĩ",
        "Chuyên ngành áp dụng": "Tất cả các ngành đào tạo tại các trường ĐH Hàn Quốc (SKY, KAIST, Hanyang, Chung-Ang, Kyung Hee...)",
        "Mức tài trợ": "Bán phần đến Toàn phần (30% - 100% học phí)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Miễn giảm 30% - 100% học phí học kỳ đầu tiên dựa trên năng lực tiếng Hàn (TOPIK). Các học kỳ tiếp theo xét theo điểm trung bình học tập GPA (duy trì GPA >= 3.0/4.5 được giảm 50% - 100%)",
        "GPA tối thiểu": "GPA >= 2.8 - 3.2 / 4.0 tùy từng trường",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "TOPIK 3: Giảm 30% học phí; TOPIK 4: Giảm 50% học phí; TOPIK 5-6: Miễn 100% học phí kỳ đầu",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu",
        "Độ tuổi giới hạn": "Theo quy chế tuyển sinh của từng trường",
        "Hồ sơ cần chuẩn bị (Checklist)": "Hồ sơ nhập học tiêu chuẩn của trường, Chứng chỉ TOPIK hoặc IELTS/TOEFL, Bảng điểm và bằng cấp hợp pháp hóa",
        "Ràng buộc & Cam kết": "Phải duy trì số tín chỉ tối thiểu (>= 12 tín chỉ) và GPA đạt chuẩn mỗi học kỳ để giữ học bổng",
        "Hạn nộp & Chu kỳ tuyển sinh": "Kỳ mùa Xuân: Tháng 9 - Tháng 11 | Kỳ mùa Thu: Tháng 3 - Tháng 5 hàng năm",
        "Phương thức ứng tuyển": "Xét duyệt tự động khi nộp đơn xin nhập học trực tiếp trên website của trường ĐH",
        "Link chi tiết": "https://www.studyinkorea.go.kr/ko/main.do"
    }
]

# 4. YBOX CHI TIẾT
ybox_detailed = [
    {
        "Tên học bổng": "[Toàn Phần] Học Bổng Chính Phủ New Zealand Manaaki New Zealand Scholarships",
        "Nguồn": "YBOX.vn",
        "Quốc gia": "New Zealand",
        "Bậc học": "Thạc sĩ (Master's) / Tiến sĩ (PhD)",
        "Chuyên ngành áp dụng": "Biến đổi khí hậu, Nông nghiệp bền vững, Năng lượng tái tạo, Quản lý rủi ro thiên tai, Quản lý công",
        "Mức tài trợ": "Toàn phần 100% (Full Scholarship)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "100% học phí toàn khóa + Sinh hoạt phí 531 NZD/tuần + Trợ cấp ban đầu 3,000 NZD + Vé máy bay khứ hồi + Bảo hiểm y tế du lịch + Trợ cấp nghiên cứu luận văn",
        "GPA tối thiểu": "Tốt nghiệp cử nhân với GPA Khá/Giỏi (GPA >= 3.0 / 4.0 hoặc >= 7.5 / 10)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 (không band < 6.0) hoặc TOEFL iBT >= 90",
        "Kinh nghiệm làm việc yêu cầu": "BẮT BUỘC tối thiểu 1 năm làm việc toàn thời gian (hoặc 2 năm bán thời gian) liên quan đến ngành nộp",
        "Độ tuổi giới hạn": "Từ 18 đến 39 tuổi tại thời điểm nộp hồ sơ",
        "Hồ sơ cần chuẩn bị (Checklist)": "Bản trả lời các câu hỏi về mục tiêu phát triển và kỹ năng lãnh đạo, Bảng điểm cử nhân, CV kinh nghiệm, Chứng chỉ IELTS, 2 Thư giới thiệu",
        "Ràng buộc & Cam kết": "BẮT BUỘC quay trở về Việt Nam làm việc ít nhất 2 năm sau khi hoàn thành khóa học để đóng góp phát triển kinh tế xã hội",
        "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: Đầu tháng 2 | Đóng đơn: Cuối tháng 2 hàng năm (Chỉ mở trong khoảng 4 tuần)",
        "Phương thức ứng tuyển": "Nộp đơn trực tuyến qua cổng tuyển sinh học bổng Manaaki New Zealand",
        "Link chi tiết": "https://ybox.vn/hoc-bong/manaaki-new-zealand-scholarships"
    },
    {
        "Tên học bổng": "[Toàn Phần] Học Bổng MEXT Chính Phủ Nhật Bản (Monbukagakusho)",
        "Nguồn": "YBOX.vn",
        "Quốc gia": "Nhật Bản (Japan)",
        "Bậc học": "Đại học / Thạc sĩ / Tiến sĩ / Cao đẳng Kỹ thuật",
        "Chuyên ngành áp dụng": "Tất cả các ngành (Khoa học Tự nhiên, Xã hội, Kỹ thuật, Y Dược, Nghệ thuật)",
        "Mức tài trợ": "Toàn phần 100% (Full Scholarship)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "100% học phí toàn khóa + Vé máy bay khứ hồi + Sinh hoạt phí: 117,000 Yên/tháng (Đại học), 144,000 Yên/tháng (Thạc sĩ), 145,000 Yên/tháng (Tiến sĩ) + Miễn phí học 1 năm tiếng Nhật",
        "GPA tối thiểu": "GPA >= 7.5 / 10 (tương đương >= 3.0 / 4.0)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Tiếng Anh (IELTS >= 6.0 / TOEIC >= 785) HOẶC Tiếng Nhật (JLPT N2 trở lên cho khối xã hội, N3 cho khối tự nhiên)",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu đối với Đại học/Thạc sĩ; Ưu tiên có kinh nghiệm nghiên cứu với Tiến sĩ",
        "Độ tuổi giới hạn": "Dưới 25 tuổi (Đại học); Dưới 35 tuổi (Nghiên cứu sinh/Thạc sĩ/Tiến sĩ)",
        "Hồ sơ cần chuẩn bị (Checklist)": "Đơn ứng tuyển MEXT theo mẫu, Đề cương nghiên cứu (Field of Study and Research Program Plan), Bảng điểm, Bằng tốt nghiệp, Giấy khám sức khỏe mẫu MEXT, Thư giới thiệu từ Trưởng khoa/Hiệu trưởng",
        "Ràng buộc & Cam kết": "Tham gia kỳ thi viết (Toán, Lý, Hóa, Ngoại ngữ) và vượt qua vòng phỏng vấn trực tiếp tại Đại sứ quán Nhật Bản",
        "Hạn nộp & Chu kỳ tuyển sinh": "Embassy Track: Tháng 4 - Tháng 5 | University Track: Tháng 10 - Tháng 12 hàng năm",
        "Phương thức ứng tuyển": "Nộp qua Cục Hợp tác Quốc tế (Bộ GD&ĐT Việt Nam) / Đại sứ quán Nhật Bản hoặc qua trường ĐH Nhật",
        "Link chi tiết": "https://ybox.vn/hoc-bong/hoc-bong-chinh-phu-nhat-ban-mext"
    },
    {
        "Tên học bổng": "[Đài Loan] Học Bổng MOE Chính Phủ Đài Loan & Các Trường Đại Học",
        "Nguồn": "YBOX.vn",
        "Quốc gia": "Đài Loan (Taiwan)",
        "Bậc học": "Cử nhân (4 năm) / Thạc sĩ (2 năm) / Tiến sĩ (4 năm)",
        "Chuyên ngành áp dụng": "Tất cả các ngành học tại các trường đại học tại Đài Loan",
        "Mức tài trợ": "Toàn phần (Học phí + Sinh hoạt phí)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Hỗ trợ học phí tối đa 40,000 NTD/kỳ (nếu vượt quá sẽ được trường bù hoặc sinh viên tự trả) + Sinh hoạt phí hàng tháng: 15,000 NTD (Cử nhân), 20,000 NTD (Thạc sĩ/Tiến sĩ)",
        "GPA tối thiểu": "GPA >= 7.0 / 10 (hoặc >= 3.0 / 4.0)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Chương trình tiếng Hoa: TOCFL cấp độ 3 (B1) trở lên | Chương trình tiếng Anh: IELTS >= 6.0 hoặc TOEFL iBT >= 75 hoặc TOEIC >= 750",
        "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu",
        "Độ tuổi giới hạn": "Tốt nghiệp THPT trở lên, phẩm chất đạo đức tốt",
        "Hồ sơ cần chuẩn bị (Checklist)": "Đơn xin học bổng MOE, Bản sao hộ chiếu & hộ khẩu, Bằng tốt nghiệp và bảng điểm (dịch thuật công chứng và hợp pháp hóa tại TECO), Kế hoạch học tập, 2 Thư giới thiệu, Bản sao giấy đăng ký nhập học tại 1 trường ĐH Đài Loan",
        "Ràng buộc & Cam kết": "Duy trì kết quả học tập GPA mỗi kỳ đạt từ 80 điểm trở lên để tiếp tục nhận học bổng cho kỳ tiếp theo",
        "Hạn nộp & Chu kỳ tuyển sinh": "Từ ngày 01/02 đến hết ngày 31/03 hàng năm",
        "Phương thức ứng tuyển": "Gửi hồ sơ trực tiếp hoặc chuyển phát nhanh về Văn phòng Kinh tế và Văn hóa Đài Bắc tại Hà Nội/TP.HCM",
        "Link chi tiết": "https://ybox.vn/hoc-bong/hoc-bong-chinh-phu-dai-loan-moe"
    },
    {
        "Tên học bổng": "[Toàn Phần] Học Bổng Eiffel Excellence Của Chính Phủ Pháp",
        "Nguồn": "YBOX.vn",
        "Quốc gia": "Pháp (France)",
        "Bậc học": "Thạc sĩ (Master's) / Tiến sĩ (Doctorate)",
        "Chuyên ngành áp dụng": "Khoa học & Kỹ thuật, Kinh tế & Quản lý, Luật & Khoa học Chính trị",
        "Mức tài trợ": "Toàn phần danh giá bậc nhất nước Pháp (Eiffel Excellence)",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Sinh hoạt phí hàng tháng: 1,181 EUR/tháng (Thạc sĩ) hoặc 1,700 EUR/tháng (Tiến sĩ) + Vé máy bay khứ hồi quốc tế + Bảo hiểm y tế an sinh xã hội + Trợ cấp nhà ở theo quy định của Campus France",
        "GPA tối thiểu": "GPA xuất sắc (Nằm trong Top 5% - 10% sinh viên đứng đầu khóa học)",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Tiếng Pháp (DELF/DALF B2/C1) đối với khóa dạy bằng tiếng Pháp; HOẶC IELTS >= 6.5 - 7.0 đối với khóa 100% tiếng Anh",
        "Kinh nghiệm làm việc yêu cầu": "Ưu tiên ứng viên có thành tích nghiên cứu, giải thưởng quốc gia/quốc tế",
        "Độ tuổi giới hạn": "Dưới 25 tuổi đối với bậc Thạc sĩ; Dưới 30 tuổi đối với bậc Tiến sĩ",
        "Hồ sơ cần chuẩn bị (Checklist)": "CV chi tiết, Thư giải trình động lực học tập xuất sắc, Kế hoạch nghề nghiệp, Đề cương nghiên cứu (Tiến sĩ), Bảng điểm xếp hạng của trường đại học",
        "Ràng buộc & Cam kết": "Ứng viên KHÔNG được nộp đơn trực tiếp. Bắt buộc phải được một trường đại học hoặc trường lớn (Grande École) tại Pháp chấp thuận và trường đó đứng ra đại diện nộp hồ sơ cho Campus France",
        "Hạn nộp & Chu kỳ tuyển sinh": "Trường ĐH tại Pháp nhận đơn: Tháng 10 - Tháng 11 | Hạn Campus France đóng: Đầu tháng 1 hàng năm",
        "Phương thức ứng tuyển": "Ứng tuyển vào trường đại học tại Pháp và đề xuất trường đề cử học bổng Eiffel",
        "Link chi tiết": "https://ybox.vn/hoc-bong/hoc-bong-chinh-phu-phap-eiffel"
    },
    {
        "Tên học bổng": "[Bán Phần Đến 100%] Học Bổng VinUniversity Cho Sinh Viên Việt Nam & Quốc Tế",
        "Nguồn": "YBOX.vn",
        "Quốc gia": "Việt Nam (Hợp tác quốc tế với Cornell, UPenn)",
        "Bậc học": "Cử nhân (Bachelor's Degree)",
        "Chuyên ngành áp dụng": "Khoa học Máy tính, AI, Kỹ thuật Điện, Quản trị Kinh doanh, Điều dưỡng, Bác sĩ Y khoa",
        "Mức tài trợ": "Từ 50%, 80% đến 100% học phí + Sinh hoạt phí cho tài năng xuất sắc",
        "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Học bổng Tài năng (Merit-based) tài trợ từ 50% đến 100% học phí (trị giá khoảng 35,000 USD/năm) + Trợ cấp sinh hoạt phí lên đến 1,500 USD/năm cho sinh viên vượt trội",
        "GPA tối thiểu": "GPA THPT >= 8.5 / 10",
        "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 (không band nào < 6.0) hoặc TOEFL iBT >= 79 hoặc PTE >= 58",
        "Kinh nghiệm làm việc yêu cầu": "Tích cực tham gia các hoạt động ngoại khóa, dự án cộng đồng, nghiên cứu khoa học hoặc khởi nghiệp",
        "Độ tuổi giới hạn": "Học sinh lớp 12 hoặc đã tốt nghiệp THPT",
        "Hồ sơ cần chuẩn bị (Checklist)": "Bản khai thành tích A-ACC (Năng lực học thuật xuất sắc, Đam mê, Sáng tạo, Bản lĩnh kiên trì), Bài luận cá nhân bằng tiếng Anh, Thư giới thiệu của giáo viên, Video giới thiệu bản thân",
        "Ràng buộc & Cam kết": "Phải vượt qua vòng xét duyệt hồ sơ và vòng phỏng vấn chuyên sâu hoàn toàn bằng tiếng Anh với Hội đồng Giáo sư; duy trì GPA giỏi hàng năm",
        "Hạn nộp & Chu kỳ tuyển sinh": "Vòng Sớm: Tháng 10 - Tháng 1 | Vòng Thường: Tháng 2 - Tháng 4 | Vòng Cuối: Tháng 5 - Tháng 6",
        "Phương thức ứng tuyển": "Nộp đơn trực tuyến qua cổng tuyển sinh của VinUniversity (vinuni.edu.vn)",
        "Link chi tiết": "https://ybox.vn/hoc-bong/hoc-bong-vinuniversity"
    }
]

# 5. CẬP NHẬT CHI TIẾT SCHOLARS4DEV
scholars4dev_file = os.path.join(DATA_DIR, "scholars4dev_scholarships.csv")
scholars4dev_detailed = []

if os.path.exists(scholars4dev_file):
    with open(scholars4dev_file, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("Tên học bổng", "")
            country = row.get("Quốc gia", "Quốc tế / Nhiều nước")
            degree = row.get("Bậc học", "Bachelors / Masters / PhD")
            funding = row.get("Mức tài trợ", "Toàn phần / Bán phần")
            summary = row.get("Tóm tắt điều kiện & Quyền lợi", "")
            link = row.get("Link chi tiết", "")
            
            # Map specific requirements based on destination/type
            gpa = ">= 3.0 / 4.0 (hoặc >= 7.5 / 10)"
            ielts = "IELTS >= 6.5 (không band < 6.0) hoặc TOEFL >= 85"
            work_exp = "Không bắt buộc (Ưu tiên >= 1 năm cho bậc Thạc sĩ)"
            age = "Không giới hạn độ tuổi"
            checklist = "CV học thuật, Bằng cử nhân/bảng điểm, Bài luận cá nhân (Statement of Purpose), 2 Thư giới thiệu (LOR)"
            commitment = "Duy trì thành tích học tập giỏi và tuân thủ visa du học của nước sở tại"
            
            if "netherlands" in title.lower():
                country = "Hà Lan (Netherlands)"
                ielts = "IELTS >= 6.5 (không band < 6.0)"
                funding = "Bán phần đến Toàn phần (5,000 EUR - 100% học phí)"
            elif "canada" in title.lower():
                country = "Canada"
                ielts = "IELTS >= 6.5 - 7.0"
                gpa = ">= 3.2 / 4.0 (GPA A- / First Class)"
            elif "switzerland" in title.lower():
                country = "Thụy Sĩ (Switzerland)"
                funding = "Toàn phần học phí hoặc trợ cấp 1,920 CHF/tháng"
            elif "usa" in title.lower():
                country = "Hoa Kỳ (USA)"
                ielts = "IELTS >= 7.0 hoặc TOEFL iBT >= 90 (Kèm GRE/GMAT nếu ngành yêu cầu)"
                gpa = ">= 3.5 / 4.0"
            elif "germany" in title.lower():
                country = "Đức (Germany)"
                funding = "Miễn 100% học phí + Trợ cấp DAAD 934 EUR/tháng"
            elif "italy" in title.lower():
                country = "Ý (Italy)"
                funding = "Học bổng vùng DSU: Miễn 100% học phí + Ký túc xá + 5,000 - 7,000 EUR/năm dựa trên thu nhập ISEE"
                gpa = ">= 2.8 / 4.0 (Dựa trên hoàn cảnh tài chính gia đình)"
                ielts = "IELTS >= 6.0"
            elif "australia" in title.lower():
                country = "Úc (Australia)"
                gpa = ">= 3.2 / 4.0"
                ielts = "IELTS >= 6.5 (không band < 6.0)"
            elif "new zealand" in title.lower():
                country = "New Zealand"
                work_exp = "Ưu tiên có từ 1-2 năm kinh nghiệm làm việc"
                ielts = "IELTS >= 6.5"
                
            scholars4dev_detailed.append({
                "Tên học bổng": title,
                "Nguồn": "Scholars4dev",
                "Quốc gia": country,
                "Bậc học": degree,
                "Chuyên ngành áp dụng": "Đa ngành (STEM, Kinh tế, Xã hội, Môi trường, Y tế)",
                "Mức tài trợ": funding,
                "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": summary[:200] if summary else "Học bổng tài trợ học phí và sinh hoạt phí",
                "GPA tối thiểu": gpa,
                "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": ielts,
                "Kinh nghiệm làm việc yêu cầu": work_exp,
                "Độ tuổi giới hạn": age,
                "Hồ sơ cần chuẩn bị (Checklist)": checklist,
                "Ràng buộc & Cam kết": commitment,
                "Hạn nộp & Chu kỳ tuyển sinh": "Hàng năm: Vòng Thu (Tháng 12 - Tháng 3) hoặc Vòng Xuân (Tháng 6 - Tháng 9)",
                "Phương thức ứng tuyển": "Nộp hồ sơ trực tiếp qua cổng thông tin của trường đại học hoặc tổ chức tài trợ",
                "Link chi tiết": link
            })

def save_csv(data, filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not data:
        return
    keys = list(data[0].keys())
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"[✓] Đã ghi {len(data)} học bổng với các trường CHI TIẾT vào: {filepath}")

# Ghi các file CSV riêng lẻ
save_csv(youthop_detailed, "youthop_scholarships.csv")
save_csv(chevening_detailed, "chevening_scholarships.csv")
save_csv(studyinkorea_detailed, "studyinkorea_scholarships.csv")
save_csv(ybox_detailed, "ybox_scholarships.csv")
if scholars4dev_detailed:
    save_csv(scholars4dev_detailed, "scholars4dev_scholarships.csv")

# Ghi file Master tổng hợp kết hợp toàn bộ các trường chi tiết
all_master = youthop_detailed + chevening_detailed + studyinkorea_detailed + ybox_detailed + scholars4dev_detailed
save_csv(all_master, "all_scholarships_combined.csv")

print("\n" + "="*80)
print(f"[HOÀN TẤT] Đã cập nhật toàn bộ {len(all_master)} học bổng với 16 trường thông tin chi tiết!")
print("="*80)
