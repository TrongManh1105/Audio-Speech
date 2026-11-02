# CSE457 - XỬ LÝ ÂM THANH VÀ TIẾNG NÓI (AUDIO & SPEECH PROCESSING)
**Trường Đại học Thủy Lợi — Khoa Công nghệ Thông tin — Bộ môn Trí tuệ Nhân tạo**  
**Sinh viên thực hiện:** Nguyễn Trọng Mạnh Tiền
**Mã sinh viên:** 2351260689 | **Lớp:** 65TTNT (Trí tuệ nhân tạo K65)  
**Giảng viên hướng dẫn:** Bộ môn Trí tuệ Nhân tạo - CSE457  

---

## 📌 BẢNG TỔNG HỢP NỘI DUNG 4 BÀI THỰC HÀNH

| Bài Lab | Chuyên đề | Kỹ thuật cốt lõi | Dữ liệu thực nghiệm | File mã nguồn |
| :--- | :--- | :--- | :--- | :--- |
| **Lab 1** | **Phân tích & Xử lý Tín hiệu Âm thanh Số** | Lấy mẫu, Nyquist, RMS/Peak, FFT, STFT, Cửa sổ, Bộ lọc FIR, Lượng tử hóa, SNR, Resampling, PCM vs MP3 | `audio/input.wav` (Stereo 44.1 kHz) | [`Lab1.ipynb`](Lab1.ipynb)<br>[`Lab01.py`](Lab01.py) |
| **Lab 2** | **Đặc trưng Tiếng nói & Nhận dạng bằng DTW** | Short-Time Energy, ZCR, Endpoint Detection, 13 MFCC, CMN, Dynamic Time Warping (DTW), Nearest-Template | `dataset/` (5 từ số đếm x 5 lần lặp = 25 file 16 kHz) | [`Lab2.ipynb`](Lab2.ipynb)<br>[`Lab02.py`](Lab02.py) |
| **Lab 3** | **Nhận dạng Tiếng nói Nâng cao với HMM** | 39-D MFCC động ($\text{MFCC} + \Delta + \Delta^2$), Left-to-Right Gaussian HMM, Baum-Welch (EM), Viterbi Alignment, Lexicon, Bigram MAP Re-ranking | `dataset_lab3/` (5 từ lệnh x 8 file = 40 file 16 kHz) | [`Lab3.ipynb`](Lab3.ipynb)<br>[`Lab03.py`](Lab03.py) |
| **Lab 4** | **Tổng hợp Tiếng nói (Text-to-Speech - TTS)** | Kiến trúc TTS, Unit Selection (Target & Join cost), Cross-fade smoothing, Source-Filter, HMM Parametric Synthesis, Neural TTS Inference, MOS Listening Test | `lab4_data/` (Kho 32 units x 16 từ vựng x 2 candidates) | [`Lab04.ipynb`](Lab04.ipynb)<br>[`Lab04.py`](Lab04.py) |

---

## 📂 CẤU TRÚC THƯ MỤC REPOSITORY

```
Audio & Speech/
├── Lab1.ipynb                   # Jupyter Notebook Lab 1 (đầy đủ biểu đồ & lý thuyết)
├── Lab01.py                     # Script Python chạy tự động toàn bộ Lab 1
├── Lab2.ipynb                   # Jupyter Notebook Lab 2 (đầy đủ biểu đồ & lý thuyết)
├── Lab02.py                     # Script Python chạy tự động toàn bộ Lab 2
├── Lab3.ipynb                   # Jupyter Notebook Lab 3 (đầy đủ biểu đồ & lý thuyết)
├── Lab03.py                     # Script Python chạy tự động toàn bộ Lab 3
├── Lab04.ipynb                  # Jupyter Notebook Lab 4 (đầy đủ biểu đồ & lý thuyết)
├── Lab04.py                     # Script Python chạy tự động toàn bộ Lab 4
│
├── audio/                       # Âm thanh phục vụ và kết xuất từ Lab 1
│   ├── input.wav                # Tệp âm thanh thử nghiệm gốc (44.1 kHz stereo)
│   ├── filtered_lowpass_2k.wav  # Âm thanh sau lọc thông thấp FIR 2 kHz
│   ├── filtered_highpass_1k.wav # Âm thanh sau lọc thông cao FIR 1 kHz
│   ├── quantized_4bit.wav       # Âm thanh lượng tử hóa 4-bit (nhiễu lượng tử cao)
│   ├── quantized_8bit.wav       # Âm thanh lượng tử hóa 8-bit
│   ├── resampled_16k.wav        # Âm thanh downsample về 16 kHz
│   └── resampled_8k.wav         # Âm thanh downsample về 8 kHz
│
├── dataset/                     # Tập dữ liệu từ vựng số đếm Lab 2 (16 kHz mono)
│   ├── khong/                   # 5 file phát âm từ 'không' (khong_01.wav ... 05.wav)
│   ├── mot/                     # 5 file phát âm từ 'một'
│   ├── hai/                     # 5 file phát âm từ 'hai'
│   ├── ba/                      # 5 file phát âm từ 'ba'
│   └── bon/                     # 5 file phát âm từ 'bốn'
│
├── dataset_lab3/                # Tập dữ liệu lệnh điều khiển Lab 3 (16 kHz mono)
│   ├── train/                   # 6 file train cho mỗi lệnh: mo, dong, len, xuong, dung
│   └── test/                    # 2 file test cho mỗi lệnh: mo, dong, len, xuong, dung
│
├── lab4_data/                   # Kho dữ liệu và backend Lab 4
│   ├── units/                   # Kho 32 unit âm thanh (16 từ vựng x 2 giọng đọc ứng viên)
│   ├── metadata.csv             # Bảng thông số: unit_id, label, speaker, duration, rms
│   ├── hmm_tts_backend.py       # Module backend tổng hợp HMM tham số
│   └── neural_tts_backend.py    # Module backend suy luận Neural TTS
│
├── audio_output/                # File âm thanh kết xuất từ Lab 4
│   ├── raw_concat.wav           # Baseline ghép thẳng (click biên nối)
│   ├── best_concat.wav          # Tối ưu sau Unit Selection & Cross-fade 15ms
│   ├── hmm_tts.wav              # Kết quả HMM Parametric TTS
│   ├── neural_tts.wav           # Kết quả Deep Learning Neural TTS
│   ├── crossfade_*.wav          # Thử nghiệm các mức làm mượt 0ms, 5ms, 15ms, 30ms
│   └── speed_*.wav, pitch_*.wav # Thử nghiệm biến đổi Prosody
│
├── figures_lab1/                # Toàn bộ biểu đồ phân tích thực nghiệm Lab 1
├── figures_lab2/                # Toàn bộ biểu đồ phân tích thực nghiệm Lab 2
├── figures_lab3/                # Toàn bộ biểu đồ phân tích thực nghiệm Lab 3
├── figures/                     # Toàn bộ biểu đồ phân tích thực nghiệm Lab 4
│
├── results.csv                  # Bảng kết quả dự đoán chi tiết tập test của Lab 2
├── ratings.csv                  # Kết quả Listening Test đánh giá MOS của Lab 4
├── lexicon.txt                  # Từ điển phát âm mini của Lab 3
├── Bao_Cao_Lab4.md              # Báo cáo chuyên sâu 5-8 trang cho Lab 4
└── README.md                    # Tài liệu tổng quan toàn bộ 4 bài thực hành
```

---

## 🔍 CHI TIẾT NỘI DUNG VÀ KẾT QUẢ TỪNG BÀI LAB

### 1️⃣ LAB 1: PHÂN TÍCH VÀ XỬ LÝ TÍN HIỆU ÂM THANH SỐ

#### Mục tiêu & Phương pháp
Chuyển đổi tín hiệu âm thanh tương tự sang biểu diễn số; phân tích đa miền (thời gian, tần số, thời gian-tần số); thiết kế bộ lọc số FIR; khảo sát lượng tử hóa $B$-bit và nguyên lý mã hóa nén âm thanh.

#### Chuỗi thực nghiệm A $\to$ G
* **Phần A (Đọc & kiểm tra tệp):** Đọc file âm thanh stereo $44.1\text{ kHz}$, trích xuất metadata ($F_s$, channels, duration, bit depth, file size), chuyển về mono chuẩn hóa $[-1.0, 1.0]$.
* **Phần B (Miền thời gian):** Tính Peak, RMS, Năng lượng $E = \sum x^2[n]$; kiểm tra rủi ro clipping; vẽ waveform toàn tệp và zoom đoạn $1.0\text{ s} - 2.0\text{ s}$.
* **Phần C (Phân tích phổ FFT):** Áp dụng cửa sổ Hamming cho đoạn ổn định; so sánh $N_{\text{FFT}} = 2048$ và $N_{\text{FFT}} = 8192$; làm rõ sự khác biệt giữa khoảng cách bin tần số $\Delta f = F_s / N_{\text{FFT}}$ và độ phân giải vật lý thực tế $\Delta f_{\text{true}} \approx 1/T_w$; xác định các đỉnh hài âm điều hòa.
* **Phần D (STFT & Spectrogram):** So sánh 3 độ dài khung $10\text{ ms}$, $25\text{ ms}$, $50\text{ ms}$; phân tích hiện tượng đánh đổi giữa độ phân giải thời gian và độ phân giải tần số (*time-frequency trade-off*).
* **Phần E (Thí nghiệm cửa sổ):** So sánh cửa sổ Chữ nhật (Rectangular) và Hamming; chứng minh Hamming giảm rò rỉ phổ (*spectral leakage*) từ $-13\text{ dB}$ xuống $-43\text{ dB}$ nhưng làm nở rộng búp sóng chính (*main-lobe*).
* **Phần F (Bộ lọc số FIR):** Thiết kế FIR Low-pass ($f_c = 2\text{ kHz}$) và FIR High-pass ($f_c = 1\text{ kHz}$) với $M = 201\text{ taps}$ đối xứng; tính độ trễ nhóm tuyến tính $\tau_g = \frac{M-1}{2F_s} \approx 2.27\text{ ms}$; xuất file wav và đối chứng phổ trước/sau lọc.
* **Phần G (Lượng tử hóa & Mã hóa):** Lượng tử hóa tín hiệu ở $B \in \{4, 6, 8, 12, 16\}\text{ bit}$; kiểm chứng quy luật $6\text{ dB/bit}$: $\text{SNR}_Q \approx 6.02B + 4.77 - 20\log_{10}(X_{\max}/\sigma_x)$; resample về $16\text{ kHz}$ và $8\text{ kHz}$; so sánh tốc độ bit và tỷ lệ nén PCM vs MP3.

#### Bảng kết quả lượng tử hóa và nén
| Số bit ($B$) | SNR thực tế | SNR lý thuyết | Tốc độ bit (Stereo) | Mức nén so với MP3 128k |
| :---: | :---: | :---: | :---: | :---: |
| **4-bit** | $19.49\text{ dB}$ | $20.64\text{ dB}$ | $352.8\text{ kbps}$ | — |
| **8-bit** | $44.65\text{ dB}$ | $44.72\text{ dB}$ | $705.6\text{ kbps}$ | — |
| **16-bit (CD)** | **$92.90\text{ dB}$** | **$92.88\text{ dB}$** | **$1,411.2\text{ kbps}$** | **$11.03 : 1$ (Tiết kiệm 90.9%)** |

---

### 2️⃣ LAB 2: ĐẶC TRƯNG TIẾNG NÓI VÀ NHẬN DẠNG BẰNG DTW

#### Mục tiêu & Phương pháp
Xây dựng trọn vẹn hệ nhận dạng từ đơn cô lập (*Isolated Word Recognition*) cho 5 số đếm tiếng Việt (*không, một, hai, ba, bốn*); tự cài đặt thuật toán đối sánh mẫu phi tuyến tính **Dynamic Time Warping (DTW)**; đánh giá độ chính xác và ma trận nhầm lẫn.

#### Chuỗi thực nghiệm A $\to$ G
* **Phần A (Dataset):** 5 lớp từ vựng $\times$ 5 lần lặp = 25 file WAV $16\text{ kHz}$ mono; chia 3 train + 2 test không rò rỉ dữ liệu.
* **Phần B (Đặc trưng thời gian):** Tính Short-Time Log-Energy ($E_r$) và Zero-Crossing Rate (ZCR) trên khung $25\text{ ms}$, bước nhảy $10\text{ ms}$; nhận diện ranh giới giữa khoảng lặng (*silence*), âm hữu thanh (*voiced*) và âm vô thanh (*unvoiced*).
* **Phần C (Endpoint Detection):** Tự động phát hiện điểm bắt đầu/kết thúc từ phát âm; cắt bỏ khoảng lặng thừa và duy trì vùng đệm an toàn $50\text{ ms}$ để bảo toàn các phụ âm yếu đầu/cuối.
* **Phần D (Trích xuất MFCC):** Tiền nhấn $\alpha = 0.97 \implies y[n] = x[n] - 0.97x[n-1]$; phân tích 24 bộ lọc tam giác Mel filterbank; lấy log năng lượng và biến đổi DCT thu 13 hệ số MFCC; chuẩn hóa CMN (*Cepstral Mean Normalization*); vẽ Heatmap ma trận đặc trưng.
* **Phần E (Tự cài đặt DTW):** Tính ma trận chi phí Euclidean $C[i, j]$; quy hoạch động ma trận chi phí tích lũy $D[i, j]$; truy vết đường căn chỉnh tối ưu (*optimal path*); chuẩn hóa chi phí theo độ dài đường đi: $\text{DTW}_{\text{norm}} = D[N, M] / |P|$; so sánh đường đi cùng từ vs khác từ.
* **Phần F (Bộ nhận dạng Nearest-Template):** Phân loại nhãn theo nguyên tắc láng giềng gần nhất; xuất bảng xếp hạng Top-3 khoảng cách cho các file test; lưu kết quả chi tiết ra `results.csv`.
* **Phần G (Thí nghiệm kiểm soát E1, E2, E3):**
  - **Baseline (Trim + 13 MFCC + 3 Templates):** Accuracy đạt **$100.0\%$**.
  - **Thí nghiệm E1 (Không Trim Endpoint):** Accuracy giảm xuống **$90.0\%$** do DTW lãng phí chi phí căn chỉnh khoảng lặng.
  - **Thí nghiệm E2 (Bổ sung 13 Delta):** Accuracy đạt **$100.0\%$**, tăng cường độ phân tách giữa các từ có âm cấu gần nhau.
  - **Thí nghiệm E3 (Chỉ 1 Template/từ):** Accuracy đạt **$100.0\%$** nhưng kém ổn định khi gặp người nói biến thiên tốc độ mạnh.

---

### 3️⃣ LAB 3: NHẬN DẠNG TIẾNG NÓI NÂNG CAO VỚI HMM

#### Mục tiêu & Phương pháp
Nâng cấp từ mô hình đối sánh mẫu sang mô hình xác suất thống kê theo thời gian; xây dựng bộ nhận dạng 5 lệnh điều khiển (*mở, đóng, lên, xuống, dừng*) sử dụng **Gaussian HMM** đa chiều; giải mã chuỗi trạng thái bằng **Viterbi**; tích hợp mô hình ngôn ngữ **Bigram** tái xếp hạng MAP.

#### Chuỗi thực nghiệm 4.1 $\to$ 4.8
* **Phần A (39-D Dynamic MFCCs):** Trích xuất 13 MFCC tĩnh + 13 Delta ($\Delta$) + 13 Delta-Delta ($\Delta^2$) = 39 chiều; áp dụng chuẩn hóa Utterance-level CMVN; vẽ Heatmap so sánh phân bố đặc trưng động.
* **Phần B & C (Khởi tạo & Huấn luyện HMM):** Cấu hình 5-state Left-to-Right Bakis topology ($\pi = [1, 0, 0, 0, 0]$, $a_{ii} = 0.7, a_{i, i+1} = 0.3$); sử dụng phân bố Gauss đa biến với ma trận hiệp phương sai đường chéo (`diag covariance`); huấn luyện bằng giải thuật EM (Baum-Welch); khảo sát số trạng thái $n\_states \in \{3, 5, 7\}$.
* **Phần D (Maximum Likelihood & Viterbi Alignment):** Nhận dạng theo $\hat{w} = \arg\max_w \frac{1}{T}\log P(X \mid \lambda_w)$; giải mã Viterbi state sequence; vẽ biểu đồ bậc thang thể hiện thời lượng dừng ở từng state âm học.
* **Phần E (So sánh với DTW):** HMM đạt độ chính xác **$100.0\%$** vượt trội so với DTW Baseline (**$90.0\%$**), đồng thời có tốc độ suy luận nhanh hơn nhờ nén thông tin vào các phân bố xác suất.
* **Phần F (Lexicon Mini):** Tạo và phân tích từ điển phát âm `lexicon.txt` kết nối từ ngữ với chuỗi âm vị (*phone inventory*).
* **Phần G (Bigram & MAP Re-ranking):** Xây dựng mô hình ngôn ngữ Bigram có làm trơn Add-$k$; công thức kết hợp: $\text{Score}(W) = \frac{1}{T}\log P_A(X \mid W) + \lambda_{LM}\log P_L(W)$; khảo sát ảnh hưởng khi thay đổi $\lambda_{LM} \in \{0.0, 0.1, 0.3, 1.0\}$.
* **Phần H (Đánh giá & Reject Threshold):** Vẽ Confusion Matrix đạt $100\%$ độ chính xác; phân tích phân bố log-likelihood giữa đúng lớp ($\bar{S}_{\text{correct}} = -47.67$) và sai lớp ($\bar{S}_{\text{wrong}} = -67.34$); đề xuất ngưỡng từ chối $\theta_{\text{reject}} = -57.50$ để phát hiện từ ngoài từ điển (Unknown/OOV).

---

### 4️⃣ LAB 4: TỔNG HỢP TIẾNG NÓI (TEXT-TO-SPEECH - TTS)

#### Mục tiêu & Phương pháp
Xây dựng hệ thống Mini TTS miền hẹp cho bài toán *"Thông báo xếp hàng tự động"* (câu mẫu: *"Mời khách hàng số 23 đến quầy 5."*); làm chủ và so sánh 3 thế hệ tổng hợp tiếng nói: **Concatenative TTS**, **HMM-based Parametric TTS**, và **Deep Learning Neural TTS**.

#### Chuỗi thực nghiệm A $\to$ G
* **Phần A (Text Normalization & Inventory):** Xây dựng hàm `normalize_queue_text()` chuyển chữ số sang từ đọc; chuẩn bị kho mẫu 32 units ($F_s = 16\text{ kHz}$ mono, cân bằng năng lượng RMS mục tiêu $0.0800$); vẽ biểu đồ Histogram thời lượng và RMS.
* **Phần B (Baseline Concatenation):** Ghép nối trực tiếp các đơn vị âm thanh; phát hiện tiếng lách tách (**click**) và bước nhảy pha/năng lượng tại các đường biên nối trên Waveform và Spectrogram (`raw_concat.wav`).
* **Phần C (Unit Selection & Smoothing):** Cài đặt hàm chi phí ghép nối $C_{\text{join}}$ dựa trên sai lệch phổ log-magnitude FFT $25\text{ ms}$; dùng Quy hoạch động (Viterbi) tìm đường đi tối ưu chi phí; thử nghiệm các mức Cross-fade $0, 5, 15, 30\text{ ms}$; chọn mức tối ưu $15\text{ ms}$ (`best_concat.wav`) giúp triệt tiêu hoàn toàn tiếng click mà không làm nhòe phụ âm.
* **Phần D (Prosody & Source-Filter):** Đo chu kỳ pitch $N_p = 66$ mẫu trên nguyên âm hữu thanh `/a/`, kiểm chứng công thức $F_0 = F_s / N_p \approx 242.42\text{ Hz}$; thử nghiệm Time-stretch ($0.8\times, 1.2\times$) và Pitch-shift ($\pm 2$ semitones); giải thích tại sao không được làm biến dạng vỏ phổ Formant ($H(z)$).
* **Phần E (HMM Parametric Synthesis):** Tạo bộ tổng hợp HMM phát sinh chuỗi tham số âm học liên tục ($F_0$ contour, Formants $F_1, F_2, F_3$, State sequence) và đưa qua vocoder bộ lọc cộng hưởng; nhận xét âm sắc đều đặn, liền mạch nhưng có tính kim loại (*buzzy/robotic*).
* **Phần F (Neural TTS Inference):** Thực hiện suy luận mô hình học sâu tiền huấn luyện; đo đạc độ trễ xử lý (*latency*) trên 3 câu test; trích xuất Mel-spectrogram.
* **Phần G (So sánh toàn diện & Listening Test):** Tổ chức bài kiểm tra nghe chủ quan mini MOS với 10 người nghe trên 3 câu test, lưu dữ liệu vào `ratings.csv`.

#### Bảng so sánh 3 phương pháp tổng hợp tiếng nói
| Tiêu chí đánh giá | Concatenative Synthesis (Ghép nối) | HMM Parametric Synthesis (Tham số) | Deep Learning Neural TTS (Học sâu) |
| :--- | :---: | :---: | :---: |
| **Intelligibility (Độ rõ lời)** | Cao ($96.5\%$) | Khá ($92.0\%$) | **Rất cao ($99.0\%$)** |
| **Naturalness (Điểm MOS 1–5)** | $3.84 / 5.0$ | $3.09 / 5.0$ *(buzzy)* | **$4.69 / 5.0$ (Tự nhiên như người thật)** |
| **Continuity (Độ liền mạch)** | $3.65 / 5.0$ *(vết nối cơ học)* | $4.56 / 5.0$ *(trơn tru)* | **$4.83 / 5.0$ (Ngữ điệu liên tục)** |
| **Độ trễ xử lý (Latency)** | **$< 50\text{ ms}$ (Cực nhanh)** | $\sim 120\text{ ms}$ (Nhanh) | $\sim 400 - 1500\text{ ms}$ (Phụ thuộc GPU/CPU) |
| **Dung lượng lưu trữ** | Lớn (100MB – hàng GB) | **Siêu nhẹ ($1 - 5\text{ MB}$)** | Trung bình ($20 - 100\text{ MB}$) |
| **Khả năng biến đổi giọng** | Kém (dễ méo tín hiệu) | Linh hoạt (scale tham số F0/Duration) | Cực kỳ linh hoạt (Voice cloning/Emotion) |

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT VÀ CHẠY THỬ NGHIỆM

### 1. Yêu cầu hệ thống
* Python 3.10 trở lên trên Windows, Linux hoặc macOS.
* Cài đặt các thư viện cần thiết:
```bash
pip install numpy scipy matplotlib soundfile librosa scikit-learn hmmlearn gTTS
```

### 2. Thực thi độc lập từng bài Lab bằng dòng lệnh
Bạn có thể chạy trực tiếp các file Python để tự động tái tạo dữ liệu, kết xuất file âm thanh và lưu toàn bộ biểu đồ:
```bash
# Chạy Lab 1: Phân tích tín hiệu số & Bộ lọc FIR
python Lab01.py

# Chạy Lab 2: Trích xuất MFCC & Nhận dạng từ đơn DTW
python Lab02.py

# Chạy Lab 3: Nhận dạng tiếng nói nâng cao với HMM & Bigram
python Lab03.py

# Chạy Lab 4: Tổng hợp tiếng nói TTS (Ghép nối, HMM, Neural)
python Lab04.py
```

### 3. Xem báo cáo tương tác trên Jupyter Notebook
Mỗi bài lab đều có file Notebook `.ipynb` tương ứng:
* [`Lab1.ipynb`](Lab1.ipynb) — Báo cáo trực quan Lab 1 kèm câu trả lời cho 7 câu hỏi lý thuyết.
* [`Lab2.ipynb`](Lab2.ipynb) — Báo cáo trực quan Lab 2 kèm câu trả lời cho 9 câu hỏi lý thuyết.
* [`Lab3.ipynb`](Lab3.ipynb) — Báo cáo trực quan Lab 3 kèm câu trả lời cho 10 câu hỏi lý thuyết.
* [`Lab04.ipynb`](Lab04.ipynb) — Báo cáo trực quan Lab 4 kèm câu trả lời cho 10 câu hỏi lý thuyết.

Bạn có thể mở trực tiếp các file notebook trên **GitHub Web** (đã nhúng sẵn toàn bộ hình ảnh, đồ thị phổ màu và kết quả in ra) hoặc mở bằng **VS Code / Jupyter Lab** để chạy tương tác và nghe âm thanh trực tiếp.

---

## 📚 TÀI LIỆU THAM KHẢO

1. **X. Huang, A. Acero, H.-W. Hon**, *Spoken Language Processing: A Guide to Theory, Algorithm, and System Development*, Prentice Hall, 2001.
2. **L. R. Rabiner, R. W. Schafer**, *Theory and Applications of Digital Speech Processing*, Pearson / Prentice Hall, 2011.
3. **D. Jurafsky, J. H. Martin**, *Speech and Language Processing*, 2nd / 3rd Edition, Pearson / Prentice Hall, 2008–2024.
4. **Bộ môn Trí tuệ Nhân tạo - Khoa CNTT - Đại học Thủy Lợi**, *Đề cương chi tiết học phần và bài giảng CSE457 - Xử lý Âm thanh và Tiếng nói*, 2023–2026.
