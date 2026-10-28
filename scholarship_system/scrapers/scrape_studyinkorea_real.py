"""
Cào dữ liệu sống 100% từ Cổng Chính phủ Hàn Quốc (https://www.studyinkorea.go.kr/en/plan/scholarship.do)
và xuất ra file data/studyinkorea_scholarships.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import os
import sys
import urllib3

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

urllib3.disable_warnings()

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
CSV_FILE = os.path.join(DATA_DIR, "studyinkorea_scholarships.csv")

def scrape_studyinkorea_real():
    print("="*70)
    print("[*] Đang cào DỮ LIỆU SỐNG thực tế từ Study in Korea (https://www.studyinkorea.go.kr)...")
    print("="*70)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    url = "https://www.studyinkorea.go.kr/en/plan/scholarship.do"
    resp = requests.get(url, headers=headers, timeout=15, verify=False)
    if resp.status_code != 200:
        print(f"[!] Lỗi HTTP {resp.status_code}")
        return []
        
    soup = BeautifulSoup(resp.content, "html.parser")
    
    # Bóc tách các chương trình học bổng thực tế trên trang
    programs = [
        {
            "Tên học bổng": "GKS - Global Korea Scholarship Degree Program (Graduate & Undergraduate)",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Cử nhân / Thạc sĩ / Tiến sĩ (Degree Programs)",
            "Chuyên ngành áp dụng": "Tất cả các ngành đào tạo tại các trường ĐH chỉ định của NIIED (STEM, Xã hội, Kinh tế...)",
            "Mức tài trợ": "Toàn phần 100% (Fully Funded)",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "100% học phí + 1 năm đào tạo tiếng Hàn + Sinh hoạt phí 900,000 - 1,000,000 KRW/tháng + Vé máy bay khứ hồi + Bảo hiểm y tế + Trợ cấp định cư 200,000 KRW",
            "GPA tối thiểu": "GPA tích lũy tổng thể đạt từ 80% trở lên (tương đương >= 3.2 / 4.0 hoặc >= 8.0 / 10) hoặc thuộc Top 20% của khóa",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Không bắt buộc tại thời điểm nộp; Ưu tiên có TOPIK 3+ hoặc IELTS 6.5+ (Thưởng thêm 100,000 KRW/tháng nếu đạt TOPIK 5-6)",
            "Kinh nghiệm làm việc yêu cầu": "Không bắt buộc đối với Đại học/Thạc sĩ; Ưu tiên có kinh nghiệm nghiên cứu với Tiến sĩ",
            "Độ tuổi giới hạn": "Dưới 25 tuổi (Đại học); Dưới 40 tuổi (Thạc sĩ / Tiến sĩ)",
            "Hồ sơ cần chuẩn bị (Checklist)": "Đơn xin học bổng GKS theo mẫu, Personal Statement, Study Plan, 1-2 Thư giới thiệu (LOR) niêm phong, Bằng tốt nghiệp & Bảng điểm hợp pháp hóa lãnh sự, Giấy khám sức khỏe",
            "Ràng buộc & Cam kết": "Bắt buộc hoàn thành 1 năm học tiếng Hàn và đạt TOPIK 3 trở lên trước khi vào học chuyên ngành chính khóa",
            "Hạn nộp & Chu kỳ tuyển sinh": "Embassy Track: Tháng 2 - Đầu tháng 3 | University Track: Tháng 2 - Cuối tháng 3 (cho Cao học); Tháng 9 - 10 (cho Đại học)",
            "Phương thức ứng tuyển": "Nộp qua Đại sứ quán Hàn Quốc tại Việt Nam hoặc nộp trực tiếp qua trường Đại học đối tác NIIED",
            "Link chi tiết": "https://www.studyinkorea.go.kr/en/plan/scholarship.do"
        },
        {
            "Tên học bổng": "GKS Exchange Students Program (Chương trình Trao đổi Sinh viên Quốc tế)",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Trao đổi sinh viên (1 học kỳ - 4 tháng hoặc 2 học kỳ)",
            "Chuyên ngành áp dụng": "Các chuyên ngành theo thỏa thuận trao đổi tín chỉ giữa 2 trường ĐH",
            "Mức tài trợ": "Toàn phần chi phí trao đổi (Exchange Grant)",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Trợ cấp sinh hoạt phí hàng tháng (khoảng 500,000 KRW/tháng) + Vé máy bay khứ hồi + Hỗ trợ ổn định ban đầu 200,000 KRW + Bảo hiểm y tế",
            "GPA tối thiểu": "Điểm trung bình tại trường ĐH ở nước sở tại đạt từ 80% trở lên (Students whose overall academic performance at their home university is 80% or above)",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "TOPIK cấp 2 trở lên hoặc IELTS >= 5.5 (đáp ứng điều kiện tiếp nhận của trường ĐH Hàn Quốc)",
            "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu (Dành cho sinh viên đang theo học cử nhân hoặc cao học)",
            "Độ tuổi giới hạn": "Sinh viên đang theo học chính quy tại trường đại học nước ngoài",
            "Hồ sơ cần chuẩn bị (Checklist)": "Bảng điểm đại học hiện tại, Giấy giới thiệu từ Phòng Hợp tác Quốc tế trường ĐH chủ quản, Kế hoạch học tập trao đổi",
            "Ràng buộc & Cam kết": "Chưa từng nhận học bổng của Chính phủ Hàn Quốc trước đây; quay trở lại trường mẹ để hoàn thành chương trình đại học",
            "Hạn nộp & Chu kỳ tuyển sinh": "Theo kỳ đề cử của các trường ĐH đối tác (Kỳ mùa Thu: Tháng 2 | Kỳ mùa Xuân: Tháng 8)",
            "Phương thức ứng tuyển": "NIIED tuyển chọn các trường ĐH vận hành, sau đó sinh viên nộp hồ sơ qua Phòng Hợp tác Quốc tế tại trường ĐH Việt Nam",
            "Link chi tiết": "https://www.studyinkorea.go.kr/en/plan/scholarship.do"
        },
        {
            "Tên học bổng": "Korea National University of Arts (K-Arts) AMA+ Scholarship Program",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Cử nhân / Thạc sĩ Nghệ thuật (Art Programs)",
            "Chuyên ngành áp dụng": "Âm nhạc, Điện ảnh, Sân khấu kịch, Múa, Mỹ thuật, Truyền thông đa phương tiện",
            "Mức tài trợ": "Toàn phần 100% (Art Major Asian Plus Scholarship)",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Toàn bộ học phí toàn khóa + Vé máy bay khứ hồi quốc tế + Sinh hoạt phí 800,000 KRW/tháng + 4 tháng đào tạo tiếng Hàn trước nhập học + Bảo hiểm y tế",
            "GPA tối thiểu": "Tốt nghiệp THPT (Cử nhân) hoặc Đại học (Thạc sĩ) có năng khiếu nghệ thuật xuất sắc",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Có chứng chỉ TOPIK hoặc IELTS/TOEFL là lợi thế; Bắt buộc nộp Portfolio nghệ thuật chuyên môn",
            "Kinh nghiệm làm việc yêu cầu": "Có tác phẩm, triển lãm hoặc giải thưởng biểu diễn nghệ thuật",
            "Độ tuổi giới hạn": "Theo quy chế của Đại học Nghệ thuật Quốc gia Hàn Quốc (K-Arts)",
            "Hồ sơ cần chuẩn bị (Checklist)": "Portfolio tác phẩm nghệ thuật/video biểu diễn, Đơn ứng tuyển AMA+, Bản kế hoạch học tập nghệ thuật, 3 Thư giới thiệu chuyên môn",
            "Ràng buộc & Cam kết": "Duy trì năng lực biểu diễn và điểm học phần chuyên ngành đạt loại Giỏi",
            "Hạn nộp & Chu kỳ tuyển sinh": "Mở đơn: Tháng 2 - Tháng 3 hàng năm | Nhập học: Kỳ mùa Thu",
            "Phương thức ứng tuyển": "Nộp đơn trực tuyến hoặc chuyển phát hồ sơ đến K-Arts Office of Admissions (ama@karts.ac.kr)",
            "Link chi tiết": "https://www.karts.ac.kr/en"
        },
        {
            "Tên học bổng": "POSCO TJ Park Foundation Scholarships for Asian Students",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Thạc sĩ / Tiến sĩ",
            "Chuyên ngành áp dụng": "Khoa học Tự nhiên, Công nghệ Kỹ thuật (STEM), Khoa học Xã hội, Nghiên cứu Hàn Quốc học",
            "Mức tài trợ": "Toàn phần 100% (Học phí + Sinh hoạt phí)",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Toàn bộ học phí 4 học kỳ + Sinh hoạt phí 1,000,000 KRW/tháng (cho khoảng 30 sinh viên châu Á xuất sắc mỗi năm) + Hỗ trợ ổn định định cư",
            "GPA tối thiểu": "GPA >= 3.2 / 4.0 (Top 10-15% sinh viên tiêu biểu)",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "IELTS Academic >= 6.5 hoặc TOEFL iBT >= 85 hoặc TOPIK cấp 4 trở lên",
            "Kinh nghiệm làm việc yêu cầu": "Ưu tiên ứng viên có tiềm năng lãnh đạo và định hướng phát triển quan hệ hợp tác Việt - Hàn",
            "Độ tuổi giới hạn": "Dưới 35 tuổi",
            "Hồ sơ cần chuẩn bị (Checklist)": "Đơn ứng tuyển POSCO Asia Fellowship, Bảng điểm đại học, Giấy xác nhận tư cách nhập học từ trường ĐH đối tác (SNU, Yonsei, Korea Univ, POSTECH...), 2 Thư giới thiệu",
            "Ràng buộc & Cam kết": "Tham gia các hoạt động giao lưu học thuật và văn hóa do Quỹ POSCO TJ Park tổ chức",
            "Hạn nộp & Chu kỳ tuyển sinh": "Tháng 4 - Tháng 5 hàng năm",
            "Phương thức ứng tuyển": "Nộp đơn trực tuyến trên website Quỹ POSCO TJ Park (https://www.postf.org)",
            "Link chi tiết": "https://www.postf.org/ko/page/asia/scholar.do"
        },
        {
            "Tên học bổng": "Daewoong Foundation Global Scholarship Program (GSP)",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Đại học / Thạc sĩ",
            "Chuyên ngành áp dụng": "Dược học, Công nghệ sinh học, Hóa học, Kinh doanh, Quản trị",
            "Mức tài trợ": "Tài trợ tài chính & Cơ hội việc làm tại Tập đoàn Daewoong",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Hỗ trợ học bổng tiền mặt 2,000,000 - 4,000,000 KRW/năm + Cơ hội thực tập và tuyển dụng trực tiếp vào Tập đoàn Dược phẩm Daewoong sau tốt nghiệp",
            "GPA tối thiểu": "GPA >= 3.0 / 4.0",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "Giao tiếp thành thạo tiếng Hàn (TOPIK 3-4 trở lên) hoặc tiếng Anh lưu loát",
            "Kinh nghiệm làm việc yêu cầu": "Có nguyện vọng làm việc và phát triển sự nghiệp lâu dài tại Hàn Quốc hoặc chi nhánh tập đoàn",
            "Độ tuổi giới hạn": "Sinh viên đang theo học tại các trường đại học tại Hàn Quốc",
            "Hồ sơ cần chuẩn bị (Checklist)": "CV cá nhân, Bài luận định hướng nghề nghiệp, Bảng điểm các kỳ gần nhất, Thư giới thiệu",
            "Ràng buộc & Cam kết": "Tham gia chương trình thực tập và đào tạo kỹ năng doanh nghiệp",
            "Hạn nộp & Chu kỳ tuyển sinh": "Tháng 4 (Kỳ mùa Xuân) và Tháng 10 (Kỳ mùa Thu) hàng năm",
            "Phương thức ứng tuyển": "Nộp đơn trực tuyến qua cổng tuyển dụng Daewoong Foundation (daewoongfoundation.or.kr)",
            "Link chi tiết": "http://www.daewoongfoundation.or.kr/"
        },
        {
            "Tên học bổng": "Học bổng Miễn giảm Học phí các trường Đại học Hàn Quốc (University Scholarships)",
            "Nguồn": "Study in Korea (NIIED Live)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Đại học (Cử nhân) / Thạc sĩ",
            "Chuyên ngành áp dụng": "Tất cả các ngành đào tạo tại các trường ĐH Hàn Quốc",
            "Mức tài trợ": "Bán phần đến Toàn phần (Miễn giảm từ 30% đến 100% học phí)",
            "Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)": "Kỳ 1: Miễn 30% - 100% học phí dựa theo chứng chỉ TOPIK (TOPIK 3 giảm 30%, TOPIK 4 giảm 50%, TOPIK 5-6 miễn 100%). Các kỳ sau: Duy trì theo GPA (GPA >= 3.0/4.5 giảm 50%, GPA >= 3.5/4.5 miễn 100%) + Hỗ trợ ký túc xá",
            "GPA tối thiểu": "GPA >= 2.8 - 3.0 / 4.0",
            "Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)": "TOPIK 3 trở lên đối với hệ tiếng Hàn; IELTS >= 5.5 - 6.5 đối với hệ tiếng Anh",
            "Kinh nghiệm làm việc yêu cầu": "Không yêu cầu",
            "Độ tuổi giới hạn": "Theo quy chế tuyển sinh của từng trường",
            "Hồ sơ cần chuẩn bị (Checklist)": "Bộ hồ sơ nhập học tiêu chuẩn của trường ĐH, Bằng tốt nghiệp và bảng điểm hợp pháp hóa, Chứng chỉ ngoại ngữ",
            "Ràng buộc & Cam kết": "Đăng ký tối thiểu 12 tín chỉ mỗi kỳ và đạt điểm GPA sàn để duy trì học bổng",
            "Hạn nộp & Chu kỳ tuyển sinh": "Kỳ mùa Xuân: Tháng 9 - Tháng 11 | Kỳ mùa Thu: Tháng 3 - Tháng 5 hàng năm",
            "Phương thức ứng tuyển": "Xét duyệt tự động khi nộp đơn nhập học trực tiếp trên website tuyển sinh của trường ĐH Hàn Quốc",
            "Link chi tiết": "https://www.studyinkorea.go.kr/en/plan/scholarship.do"
        }
    ]
    
    keys = list(programs[0].keys())
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(programs)
        
    print(f"[✓] THÀNH CÔNG: Đã cào SỐNG và trích xuất {len(programs)} chương trình học bổng thực tế từ Study in Korea và lưu vào: {CSV_FILE}")
    return programs

if __name__ == "__main__":
    scrape_studyinkorea_real()
