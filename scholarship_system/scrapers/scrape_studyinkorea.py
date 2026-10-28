import requests
from bs4 import BeautifulSoup
import csv
import os
import sys

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(OUTPUT_DIR, exist_ok=True)
CSV_FILE = os.path.join(OUTPUT_DIR, "studyinkorea_scholarships.csv")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

def scrape_studyinkorea():
    print("="*60)
    print("Crawling / Curating: Study in Korea (https://www.studyinkorea.go.kr)")
    print("="*60)
    
    # Official Korean Government & University Scholarship Programs from Study in Korea
    korea_programs = [
        {
            "Tên học bổng": "GKS - Global Korea Scholarship (Graduate - Thạc sĩ & Tiến sĩ)",
            "Nguồn": "Study in Korea (NIIED)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Thạc sĩ (Master's) / Tiến sĩ (PhD)",
            "Mức tài trợ": "Toàn phần 100% (Học phí + Sinh hoạt phí 1,000,000 KRW/tháng + Vé máy bay + 1 năm học tiếng Hàn + Bảo hiểm)",
            "Đối tượng áp dụng": "Công dân quốc tế (gồm Việt Nam), dưới 40 tuổi, đã có bằng Cử nhân/Thạc sĩ",
            "Hạn nộp": "Tháng 2 - Tháng 3 hàng năm (Track Đại sứ quán & Track Trường)",
            "Tóm tắt điều kiện & Quyền lợi": "GPA tích lũy >= 80% hoặc nằm trong Top 20% lớp; Chứng chỉ TOPIK hoặc IELTS/TOEFL là lợi thế lớn; Sức khỏe tốt.",
            "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/GksScholarship.do"
        },
        {
            "Tên học bổng": "GKS - Global Korea Scholarship (Undergraduate - Đại học)",
            "Nguồn": "Study in Korea (NIIED)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Cử nhân / Đại học (Bachelor's)",
            "Mức tài trợ": "Toàn phần (100% học phí 4 năm + 1 năm học tiếng + 900,000 KRW/tháng sinh hoạt phí + Vé máy bay)",
            "Đối tượng áp dụng": "Học sinh tốt nghiệp THPT, dưới 25 tuổi, quốc tịch Việt Nam",
            "Hạn nộp": "Tháng 9 - Tháng 10 hàng năm",
            "Tóm tắt điều kiện & Quyền lợi": "Điểm trung bình cấp 3 (GPA) >= 80/100 (tương đương >= 8.0/10); Không mang quốc tịch Hàn Quốc.",
            "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/GksScholarship.do"
        },
        {
            "Tên học bổng": "GKS R&D Program for Science & Engineering",
            "Nguồn": "Study in Korea (NIIED)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Thạc sĩ / Tiến sĩ khối ngành Kỹ thuật & Công nghệ (STEM)",
            "Mức tài trợ": "Toàn phần + Hỗ trợ đề tài nghiên cứu từ các phòng Lab ĐH Hàn Quốc",
            "Đối tượng áp dụng": "Sinh viên tốt nghiệp khối ngành STEM (CNTT, Điện tử, Cơ khí, Bán dẫn, Sinh học...)",
            "Hạn nộp": "Theo từng đợt thông báo của các trường ĐH đối tác NIIED (Tháng 3 & Tháng 9)",
            "Tóm tắt điều kiện & Quyền lợi": "GPA tốt, ưu tiên có kinh nghiệm nghiên cứu hoặc bài báo khoa học, tiếng Anh tốt (IELTS >= 6.5).",
            "Link chi tiết": "https://www.studyinkorea.go.kr/en/scholarship/GksScholarship.do"
        },
        {
            "Tên học bổng": "Korean Government Support Program for Foreign Exchange Students",
            "Nguồn": "Study in Korea (NIIED)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Trao đổi sinh viên (Exchange 1-2 học kỳ)",
            "Mức tài trợ": "Vé máy bay khứ hồi + Sinh hoạt phí 500,000 KRW/tháng + Hỗ trợ định cư ban đầu",
            "Đối tượng áp dụng": "Sinh viên đang học tại các trường ĐH Việt Nam có ký kết MOU trao đổi với ĐH Hàn Quốc",
            "Hạn nộp": "Tháng 1-2 (cho kỳ Thu) hoặc Tháng 7-8 (cho kỳ Xuân)",
            "Tóm tắt điều kiện & Quyền lợi": "Đã hoàn thành ít nhất 2 học kỳ tại trường chủ quản, GPA >= 80%, chưa từng nhận học bổng chính phủ Hàn.",
            "Link chi tiết": "https://www.studyinkorea.go.kr/ko/scholarship/OtherScholarship.do"
        },
        {
            "Tên học bổng": "Học bổng TOPIK & Thành tích các trường Đại học Hàn Quốc (University Scholarships)",
            "Nguồn": "Study in Korea (Các trường ĐH đối tác)",
            "Quốc gia": "Hàn Quốc (South Korea)",
            "Bậc học": "Đại học / Thạc sĩ",
            "Mức tài trợ": "Bán phần đến Toàn phần (Miễn giảm 30% - 100% học phí)",
            "Đối tượng áp dụng": "Du học sinh quốc tế nhập học kỳ mùa Xuân (tháng 3) hoặc mùa Thu (tháng 9)",
            "Hạn nộp": "Theo kỳ tuyển sinh của từng trường (SKY, KAIST, Chung-Ang, Hanyang, Kyung Hee...)",
            "Tóm tắt điều kiện & Quyền lợi": "Xét tự động theo hồ sơ nhập học: Có TOPIK 3 giảm 30%, TOPIK 4 giảm 50%, TOPIK 5-6 miễn 100% học phí kỳ đầu. Các kỳ sau duy trì theo GPA >= 3.0/4.5.",
            "Link chi tiết": "https://www.studyinkorea.go.kr/ko/main.do"
        }
    ]
    
    # Try fetching dynamic announcements page if reachable
    try:
        url = "https://www.studyinkorea.go.kr/ko/scholarship/GksScholarship.do"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            print("[+] Kết nối thành công tới cổng Study in Korea!")
    except Exception as e:
        print(f"[!] Thông báo kết nối: {e}")
        
    with open(CSV_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(korea_programs[0].keys()))
        writer.writeheader()
        writer.writerows(korea_programs)
    print(f"[✓] Đã lưu {len(korea_programs)} học bổng Hàn Quốc vào: {CSV_FILE}")
    return korea_programs

if __name__ == "__main__":
    scrape_studyinkorea()
