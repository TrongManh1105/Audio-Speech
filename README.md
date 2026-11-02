# CSE457 - Xử lý Âm thanh và Tiếng nói (Audio & Speech Processing)
**Trường Đại học Thủy Lợi - Khoa Công nghệ Thông tin - Bộ môn Trí tuệ Nhân tạo**  
**Sinh viên thực hiện:** Nguyễn Trọng Mạnh Tiến  
**Mã sinh viên:** 2351260689 | **Lớp:** 65TTNT  

---

## 📌 Tổng quan các bài thực hành trong kho lưu trữ

| Bài Lab | Tên chuyên đề | Nội dung chính | File chính |
| :--- | :--- | :--- | :--- |
| **Lab 1** | Xử lý tín hiệu cơ bản | Waveform, STFT, Spectrogram, Lọc tín hiệu, Overlap-Add (OLA) | [`Lab1.ipynb`](Lab1.ipynb) |
| **Lab 2** | Trích xuất đặc trưng âm học | Phân tích Frame, Tần số cơ bản $F_0$, Đặc trưng MFCC, Năng lượng | [`Lab2.ipynb`](Lab2.ipynb) |
| **Lab 3** | Mô hình xác suất & Nhận dạng | HMM, Dynamic Programming, Đánh giá nhận dạng tiếng nói | [`Lab3.ipynb`](Lab3.ipynb) |
| **Lab 4** | **Tổng hợp tiếng nói (TTS)** | **Kiến trúc TTS, Unit Selection, Smoothing, HMM Generation, Neural TTS** | [`Lab04.ipynb`](Lab04.ipynb), [`Lab04.py`](Lab04.py) |

---

## 🎙️ Chi tiết Bài thực hành Lab 4: TỔNG HỢP TIẾNG NÓI (Text-to-Speech)

Bài thực hành Lab 4 xây dựng hoàn chỉnh hệ thống **Mini TTS miền hẹp** cho bài toán *"Thông báo xếp hàng tại quầy giao dịch"* (Case study: *"Mời khách hàng số 23 đến quầy 5."*), đồng thời so sánh toàn diện 3 thế hệ phương pháp tổng hợp tiếng nói:
1. **Concatenative Synthesis (Ghép nối và Unit Selection)**
2. **Parametric Synthesis dựa trên HMM (HMM Generation & Source-Filter Vocoder)**
3. **Deep Learning / Neural TTS (Inference mô hình học sâu pretrained)**

### 📂 Cấu trúc thư mục Lab 4
```
Audio & Speech/
├── lab4_data/
│   ├── units/                   # Kho 32 file audio WAV 16kHz mono (16 từ vựng x 2 candidates)
│   ├── metadata.csv             # Metadata: unit_id, label, speaker, duration, rms
│   ├── hmm_tts_backend.py       # Module backend tổng hợp HMM tham số
│   └── neural_tts_backend.py    # Module backend suy luận Neural TTS
├── audio_output/                # Toàn bộ file âm thanh kết xuất từ thực nghiệm
│   ├── raw_concat.wav           # Baseline ghép thẳng (click biên nối)
│   ├── best_concat.wav          # Kết quả sau Unit Selection & Cross-fade 15ms
│   ├── hmm_tts.wav              # Kết quả HMM Parametric TTS
│   ├── neural_tts.wav           # Kết quả Neural TTS
│   ├── crossfade_*.wav          # Thử nghiệm các mức cross-fade 0ms, 5ms, 15ms, 30ms
│   └── speed_*.wav, pitch_*.wav # Thử nghiệm prosody: tốc độ và cao độ
├── figures/                     # Toàn bộ biểu đồ phân tích thực nghiệm
│   ├── inventory_stats.png      # Histogram duration và RMS của kho đơn vị
│   ├── raw_baseline_boundary.png# Waveform & Spectrogram baseline đánh dấu biên nối
│   ├── spectrogram_bien_ghep.png# So sánh Spectrogram trước và sau cross-fade
│   ├── unit_selection_join_cost.png # So sánh Join Cost giữa các đường ứng viên
│   ├── experiment_prosody_pitch_speed.png # Khảo sát biến đổi Prosody (Speed/Pitch)
│   ├── hmm_track.png            # Đồ thị F0, Formants F1/F2 và HMM states trajectory
│   └── so_sanh_output.png       # So sánh trực quan Spectrogram cả 3 phương pháp
├── ratings.csv                  # Kết quả Listening Test (MOS) với 10 người nghe
├── Bao_Cao_Lab4.md              # Báo cáo chi tiết học thuật 5-8 trang (kèm lời giải 10 câu hỏi)
├── Lab04.ipynb                  # Jupyter Notebook báo cáo tương tác đầy đủ hình ảnh & âm thanh
└── Lab04.py                     # Script Python thực thi độc lập toàn bộ bài lab
```

---

## 🚀 Hướng dẫn chạy lại mã nguồn (Reproducibility)

### 1. Cài đặt môi trường
Yêu cầu Python 3.10+:
```bash
pip install numpy scipy matplotlib soundfile librosa gTTS
```

### 2. Thực thi toàn bộ pipeline Lab 4
Chạy lệnh sau trong thư mục gốc để tự động tính toán, sinh file âm thanh và vẽ biểu đồ:
```bash
python Lab04.py
```

### 3. Xem báo cáo tương tác
Mở file [`Lab04.ipynb`](Lab04.ipynb) trên VS Code, Jupyter Notebook hoặc trực tiếp trên giao diện web GitHub để xem đầy đủ các biểu đồ spectrogram màu, đồ thị trajectory tham số và nghe audio trực tiếp qua trình phát âm thanh HTML5.

---

## 📊 Bảng so sánh tổng hợp 3 phương pháp TTS

| Tiêu chí | Concatenative Synthesis | HMM-based Parametric | Neural TTS |
| :--- | :---: | :---: | :---: |
| **Intelligibility (Độ rõ)** | Cao (96.5%) | Khá (92.0%) | **Rất cao (99.0%)** |
| **Naturalness (Điểm MOS)** | 3.84 / 5.0 | 3.09 / 5.0 *(buzzy)* | **4.69 / 5.0** |
| **Continuity (Độ liền mạch)** | 3.65 / 5.0 *(có vết nối)* | 4.56 / 5.0 *(rất trơn)* | **4.83 / 5.0** |
| **Latency (Độ trễ xử lý)** | **< 50 ms (Cực nhanh)** | ~120 ms (Nhanh) | ~400 - 1500 ms |
| **Dung lượng lưu trữ** | Lớn (100MB - hàng GB) | **Cực nhỏ (1 - 5 MB)** | Trung bình (20 - 100 MB) |
| **Khả năng biến đổi giọng** | Kém (dễ méo âm thanh) | Linh hoạt (scale tham số) | Rất linh hoạt (Voice cloning) |

Xem phân tích chuyên sâu và trả lời 10 câu hỏi lý thuyết tại file [`Bao_Cao_Lab4.md`](Bao_Cao_Lab4.md).
