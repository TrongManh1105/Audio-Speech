# HỆ THỐNG GỢI Ý HỌC BỔNG DU HỌC & PHÂN TÍCH TIÊU CHÍ (GAP ANALYSIS)

Hệ thống được thiết kế theo mô hình **Khuyến nghị kết hợp (Hybrid Recommender System)** và **Phân tích khoảng cách tiêu chuẩn (Gap Analysis)**.

---

## 1. Cấu trúc 16 trường thông tin chi tiết trong các file CSV

Tất cả các file CSV (từng nguồn và file tổng hợp) hiện đã được chuẩn hóa với đầy đủ **16 trường dữ liệu chi tiết**:

1. **`Tên học bổng`**: Tên chính thức của chương trình học bổng.
2. **`Nguồn`**: Tên nền tảng (Youth Opportunities, Chevening, Study in Korea, YBOX, Scholars4dev).
3. **`Quốc gia`**: Điểm đến du học (Hàn Quốc, Anh, Úc, Đức, Thụy Điển, Pháp, Nhật Bản...).
4. **`Bậc học`**: Cử nhân (Đại học), Thạc sĩ, Tiến sĩ, Trao đổi sinh viên.
5. **`Chuyên ngành áp dụng`**: Các khối ngành chấp nhận (STEM, AI, Kinh tế, Mọi ngành...).
6. **`Mức tài trợ`**: Toàn phần 100% (Full-ride) hoặc Bán phần.
7. **`Chi tiết quyền lợi (Học phí, Sinh hoạt phí, Vé máy bay)`**: Bóc tách chính xác số tiền trợ cấp, vé máy bay, bảo hiểm.
8. **`GPA tối thiểu`**: Ngưỡng điểm học tập sàn (thang 4.0, thang 10 hoặc phần trăm %).
9. **`Yêu cầu ngoại ngữ (IELTS/TOEFL/TOPIK)`**: Điểm sàn chứng chỉ ngoại ngữ bắt buộc.
10. **`Kinh nghiệm làm việc yêu cầu`**: Số năm/giờ làm việc bắt buộc (ví dụ: Chevening cần 2,800 giờ).
11. **`Độ tuổi giới hạn`**: Quy định về độ tuổi tối đa/tối thiểu của từng chương trình.
12. **`Hồ sơ cần chuẩn bị (Checklist)`**: Danh mục chi tiết các giấy tờ cần nộp (CV, SOP, LOR, Proposal...).
13. **`Ràng buộc & Cam kết`**: Điều kiện sau tốt nghiệp (về nước 2 năm, duy trì GPA mỗi kỳ...).
14. **`Hạn nộp & Chu kỳ tuyển sinh`**: Tháng mở đơn, hạn chót và chu kỳ tuyển sinh hàng năm.
15. **`Phương thức ứng tuyển`**: Nộp qua Đại sứ quán, Cổng trực tuyến chính phủ hay nộp trực tiếp cho trường.
16. **`Link chi tiết`**: Đường dẫn trực tiếp đến trang thông báo chính thức.

---

## 2. Dữ liệu đã xuất ra các file CSV riêng biệt

Toàn bộ dữ liệu nằm tại: `d:\Audio & Speech\scholarship_system\data/`

| STT | Nguồn dữ liệu | File CSV chi tiết |
|---|---|---|
| 1 | **Youth Opportunities** | [`youthop_scholarships.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/youthop_scholarships.csv) |
| 2 | **Chevening (UK Government)** | [`chevening_scholarships.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/chevening_scholarships.csv) |
| 3 | **Study in Korea (NIIED)** | [`studyinkorea_scholarships.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/studyinkorea_scholarships.csv) |
| 4 | **YBOX.vn** | [`ybox_scholarships.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/ybox_scholarships.csv) |
| 5 | **Scholars4dev** | [`scholars4dev_scholarships.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/scholars4dev_scholarships.csv) |
| ★ | **File Master tổng hợp** | [`all_scholarships_combined.csv`](file:///d:/Audio%20&%20Speech/scholarship_system/data/all_scholarships_combined.csv) |

---

## 2. Cấu trúc thư mục mã nguồn

```
d:\Audio & Speech\scholarship_system/
├── data/                                 # Chứa tất cả 5 file CSV riêng và file combined
│   ├── chevening_scholarships.csv
│   ├── scholars4dev_scholarships.csv
│   ├── studyinkorea_scholarships.csv
│   ├── ybox_scholarships.csv
│   ├── youthop_scholarships.csv
│   └── all_scholarships_combined.csv
├── scrapers/                             # Bộ crawler cho từng nguồn
│   ├── scrape_scholars4dev.py
│   ├── scrape_chevening.py
│   ├── scrape_youthop.py
│   ├── scrape_ybox.py
│   └── scrape_studyinkorea.py
├── run_all_crawlers.py                   # Script chạy toàn bộ 5 crawler một lúc
├── models.py                             # Data schema chuẩn hóa cho học bổng
├── recommender.py                        # Thuật toán matching & Gap Analysis
└── README.md                             # Tài liệu kỹ thuật
```

---

## 3. Cách chạy hệ thống

### Chạy crawler cập nhật dữ liệu:
```bash
cd "d:\Audio & Speech\scholarship_system"
python run_all_crawlers.py
```

### Chạy kiểm tra gợi ý học bổng & Gap Analysis:
```bash
python recommender.py
```
