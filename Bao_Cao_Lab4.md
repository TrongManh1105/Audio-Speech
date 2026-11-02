# BÁO CÁO THỰC HÀNH LAB 4
## TỔNG HỢP TIẾNG NÓI (TEXT-TO-SPEECH)
### Từ kiến trúc TTS, ghép nối và unit selection đến tổng hợp tham số HMM và TTS học sâu

* **Môn học:** CSE457 – Xử lý Âm thanh và Tiếng nói
* **Học viện / Trường:** Trường Đại học Thủy Lợi – Khoa Công nghệ Thông tin – Bộ môn Trí tuệ Nhân tạo
* **Sinh viên thực hiện:** Nguyễn Trọng Mạnh Tiến
* **Mã sinh viên:** 2351260689
* **Lớp:** 65TTNT (Trí tuệ nhân tạo K65)
* **Ngày thực hiện:** Tháng 11 / 2026

---

## 1. MỤC TIÊU VÀ TỔNG QUAN HỆ THỐNG

### 1.1. Mục tiêu bài thực hành
Bài thực hành Lab 4 giúp sinh viên kết nối chuỗi kiến thức từ xử lý tín hiệu âm thanh cơ bản (waveform, STFT, OLA ở Lab 1), trích xuất đặc trưng âm học ($F_0$, MFCC ở Lab 2), và mô hình chuỗi xác suất (HMM ở Lab 3) để giải quyết bài toán ngược: **tổng hợp tiếng nói từ văn bản (Text-to-Speech - TTS)**.

Sau bài thực hành, sinh viên đạt được các chuẩn đầu ra:
1. Mô tả và làm chủ chuỗi xử lý TTS: $\text{Text Analysis} \to \text{Phonetic Analysis} \to \text{Prosody} \to \text{Synthesis Backend} \to \text{Waveform}$.
2. Cài đặt hoàn chỉnh hệ thống mini TTS miền hẹp cho bài toán *"Thông báo xếp hàng tại quầy giao dịch"*.
3. Hiểu và triển khai thuật toán **Unit Selection** với hàm chi phí đích (*target cost*) và chi phí ghép nối (*join cost*) thông qua Quy hoạch động (Dynamic Programming).
4. Khắc phục hiện tượng gián đoạn phổ và tiếng "click" biên nối bằng kỹ thuật **Cross-fade / Overlap-Add (OLA)**.
5. Kiểm chứng vai trò của tần số cơ bản $F_0$, thời lượng (*duration*), năng lượng (*energy*) và mô hình **Source–Filter**.
6. Khảo sát chế độ phát sinh (*generation mode*) của mô hình tham số **HMM** với các đường tham số âm học biến thiên liên tục (*trajectories*).
7. Thực thi suy luận (*inference*) với mô hình TTS học sâu tiền huấn luyện (**Neural TTS**) và đo đạc độ trễ thời gian thực (*latency*).
8. Đánh giá chất lượng và so sánh toàn diện 3 thế hệ TTS dựa trên các tiêu chí: *Intelligibility*, *Naturalness*, *Continuity*, *Latency* và *Resource / Footprint*.

---

## 2. CƠ SỞ LÝ THUYẾT VÀ CÔNG THỨC TOÁN HỌC

### 2.1. Kiến trúc tổng quát của hệ Text-to-Speech
Một hệ thống TTS hoàn chỉnh gồm hai phân hệ chính:
1. **Front-End:**
   - **Text Normalization:** Biến đổi văn bản thô $T$ chứa chữ số, chữ viết tắt, ký hiệu thành chuỗi token từ ngữ $W = (w_1, w_2, \dots, w_K)$.
   - **Phonetic Analysis (G2P):** Chuyển từ thành chuỗi âm vị $P = (p_1, p_2, \dots, p_L)$. Trong bài toán miền hẹp từ vựng cố định, ta sử dụng đơn vị từ (*word-unit*).
   - **Prosodic Analysis:** Xác định nhịp điệu, trọng âm, đường cao độ cơ bản $F_0(t)$, thời lượng $d$ và đường biên độ/năng lượng $A(t)$.
2. **Back-End:** Phát sinh tín hiệu dạng sóng âm thanh (*waveform*) dựa trên đại diện âm học từ front-end.

### 2.2. Tần số cơ bản ($F_0$) và Mô hình Nguồn – Bộ lọc (Source–Filter Model)
* **Tần số cơ bản $F_0$:** Với tín hiệu tiếng nói hữu thanh (*voiced speech*), chu kỳ pitch $N_p$ (tính theo số mẫu) tại tần số lấy mẫu $F_s$ thỏa mãn:
  $$F_0 = \frac{F_s}{N_p}$$
* **Mô hình Source–Filter (Rabiner & Schafer):**
  $$X(z) = E(z) \cdot H(z)$$
  - $E(z)$: Nguồn kích thích (*Excitation*). Đối với âm hữu thanh (*voiced*), $e[n]$ là chuỗi xung tuần hoàn theo pitch period $T_0 = 1/F_0$; đối với âm vô thanh (*unvoiced*), $e[n]$ là nhiễu trắng ngẫu nhiên.
  - $H(z) = \frac{B(z)}{A(z)} = \frac{b_0 + \sum b_k z^{-k}}{1 - \sum a_k z^{-k}}$: Bộ lọc thanh quản và khoang miệng (*Vocal Tract Filter*), quyết định vỏ phổ (*spectral envelope*) và các tần số cộng hưởng formant ($F_1, F_2, F_3$).

### 2.3. Concatenative Synthesis và Thuật toán Unit Selection
Mục tiêu là tìm chuỗi ứng viên $\theta^* = (\theta_1, \theta_2, \dots, \theta_J)$ từ kho mẫu (*inventory*) sao cho tổng chi phí là nhỏ nhất:
$$\theta^* = \arg\min_{\{\theta_1 \dots \theta_J\}} \left[ \sum_{j=1}^J C_{\text{target}}(\theta_j, t_j) + \lambda \sum_{j=1}^{J-1} C_{\text{join}}(\theta_j, \theta_{j+1}) \right]$$
* **Target Cost ($C_{\text{target}}$):** Đánh giá mức độ phù hợp của candidate $\theta_j$ đối với yêu cầu ngữ cảnh $t_j$.
* **Join Cost ($C_{\text{join}}$):** Đo độ lệch phổ log-magnitude tại biên nối giữa cuối unit $\theta_j$ (độ dài $m$) và đầu unit $\theta_{j+1}$ (độ dài $1$):
  $$C_{\text{join}}(\theta_j, \theta_{j+1}) = \frac{1}{K} \sum_{k=1}^K \left[ L_{\text{left}}[k] - L_{\text{right}}[k] \right]^2 + \beta \left| \text{RMS}_{\text{left}} - \text{RMS}_{\text{right}} \right|$$
  trong đó $L[k] = 20 \log_{10} |X[k]|$ là phổ Fourier sau khi nhân cửa sổ Hanning $20-30\text{ ms}$.

### 2.4. Kỹ thuật làm mượt biên nối (Boundary Smoothing)
Khi ghép trực tiếp hai waveform $x_1$ và $x_2$, sự không trùng khớp về pha hoặc mức DC gây ra hiện tượng gián đoạn phổ và tiếng "click". Áp dụng phép nội suy **Cross-fade** trong vùng chồng lấn $N$ mẫu với ramp tuyến tính $\alpha[n] = n/N$:
$$y[n] = (1 - \alpha[n]) x_1[n] + \alpha[n] x_2[n], \quad 0 \le n < N$$

### 2.5. HMM-based Parametric Synthesis
Khác với bài toán nhận dạng tiếng nói (ASR) dùng giải thuật Viterbi để giải mã chuỗi state từ quan sát, trong HMM TTS:
- Chuỗi token xác định chuỗi trạng thái HMM.
- Mô hình chạy ở chế độ **Generation**: sinh chuỗi tham số âm học $\hat{O}^*$ cực đại hóa hàm hợp lý:
  $$\hat{O}^* = \arg\max_O P(O \mid \lambda, \text{state sequence}), \quad \text{với } \hat{O}_t = [c_t, \Delta c_t]$$
- Việc kết hợp đặc trưng động $\Delta c_t = c_t - c_{t-1}$ giúp các đường trajectory $F_0(t)$ và Formant $F_1(t), F_2(t)$ biến thiên liên tục và trơn tru qua các biên giới state.

---

## 3. THIẾT KẾ THỰC NGHIỆM VÀ QUY TRÌNH TRIỂN KHAI

### 3.1. Cấu trúc thư mục dự án
Hệ thống được tổ chức khoa học theo đúng đặc tả của bài lab:
```
Audio & Speech/
├── lab4_data/
│   ├── units/               # Kho 32 file audio WAV (16 từ vựng x 2 candidates)
│   ├── metadata.csv         # Bảng thông số label, speaker, duration, RMS
│   ├── hmm_tts_backend.py   # Backend tổng hợp HMM parametric
│   └── neural_tts_backend.py# Backend tổng hợp Neural TTS
├── audio_output/            # Các file âm thanh xuất ra từ thực nghiệm
│   ├── raw_concat.wav       # Baseline ghép thẳng
│   ├── best_concat.wav      # Kết quả sau Unit Selection & Cross-fade 15ms
│   ├── hmm_tts.wav          # Kết quả HMM Parametric TTS
│   ├── neural_tts.wav       # Kết quả Deep Learning Neural TTS
│   └── crossfade_*.wav, speed_*.wav, pitch_*.wav
├── figures/                 # 5+ hình ảnh đồ thị phân tích chất lượng cao
├── ratings.csv              # Dữ liệu đánh giá Listening Test (MOS)
├── Lab04.ipynb              # Jupyter Notebook báo cáo tương tác đầy đủ
├── Lab04.py                 # Mã nguồn Python chạy tự động
└── README_LAB4.md           # Hướng dẫn chi tiết
```

### 3.2. Chuẩn bị kho dữ liệu âm thanh (Inventory)
- **Tập từ vựng miền hẹp:** Gồm 16 từ: `mời`, `khách`, `hàng`, `số`, `không`, `một`, `hai`, `ba`, `bốn`, `năm`, `sáu`, `bảy`, `tám`, `chín`, `đến`, `quầy`.
- **Định dạng âm thanh:** Chuẩn $F_s = 16000\text{ Hz}$, mono, 16-bit PCM.
- **Xử lý silence:** Cắt bỏ khoảng lặng dư thừa (*top_db = 28dB*) và chèn khoảng lặng biên chuẩn $100\text{ ms}$ ở đầu/cuối unit.
- **Chuẩn hóa biên độ:** Cân bằng năng lượng RMS mục tiêu ở mức $\text{RMS} = 0.080$ để tránh chênh lệch âm lượng khi ghép.
- **Ứng viên:** Mỗi từ vựng có 2 candidate:
  * Candidate 01: Giọng Nữ Bắc chuẩn (`vi-VN-HoaiMyNeural`).
  * Candidate 02: Giọng Nam Bắc chuẩn (`vi-VN-NamMinhNeural`).

---

## 4. KẾT QUẢ THỰC NGHIỆM VÀ PHÂN TÍCH

### 4.1. Phần A: Phân tích Inventory
Câu thử nghiệm: *"Mời khách hàng số 23 đến quầy 5."*  
Sau khi qua hàm `normalize_queue_text()`, văn bản được chuẩn hóa thành 9 token:
`['mời', 'khách', 'hàng', 'số', 'hai', 'ba', 'đến', 'quầy', 'năm']`

* **Thống kê Inventory:**
  - Tổng số unit: 32 files.
  - Thời lượng trung bình: $0.548\text{ s}$ (ngắn nhất: `khach_01` $0.392\text{ s}$; dài nhất: `moi_01` $0.616\text{ s}$).
  - Mức RMS sau chuẩn hóa: Đồng đều tuyệt đối ở mức $0.0800$, đảm bảo khi ghép nối không xảy ra hiện tượng từ to từ nhỏ đột ngột.
* **Hình 1 (Histogram):** Lưu tại `figures/inventory_stats.png`. Biểu đồ cho thấy phân bố thời lượng tập trung tự nhiên trong khoảng $0.5 - 0.6\text{ s}$, không có giá trị dị biệt (*outlier*).

### 4.2. Phần B: Baseline Concatenation
Ghép trực tiếp các unit candidate 01 cố định không dùng cross-fade:
* File xuất ra: `audio_output/raw_concat.wav`.
* Các vị trí biên nối ghi nhận tại: $0.616\text{ s}, 1.008\text{ s}, 1.560\text{ s}, 2.080\text{ s}, 2.632\text{ s}, 3.184\text{ s}, 3.736\text{ s}, 4.288\text{ s}$.
* **Phân tích âm học:**
  - Khi nghe thực tế, tại các vị trí biên nối xuất hiện tiếng lách tách rõ rệt (**click**).
  - Trên biểu đồ Spectrogram (`figures/raw_baseline_boundary.png`), các đường vạch thẳng đứng thể hiện sự gián đoạn đột ngột của năng lượng phổ và bước nhảy pha giữa cuối từ trước và đầu từ sau.

### 4.3. Phần C: Unit Selection và Boundary Smoothing
* **Kết quả Dynamic Programming:**
  Thuật toán Viterbi đã tìm được đường đi có tổng chi phí nhỏ nhất:
  $$\text{moi\_01} \to \text{khach\_01} \to \text{hang\_01} \to \text{so\_01} \to \text{hai\_01} \to \text{ba\_01} \to \text{den\_01} \to \text{quay\_01} \to \text{nam\_01}$$
  Tổng chi phí tối ưu: $0.450$. Thuật toán đã tự động chọn toàn bộ chuỗi cùng speaker để tránh phạt chi phí đổi giọng (được gán trọng số $35.0$).
* **Thử nghiệm các mức Cross-fade ($0, 5, 15, 30\text{ ms}$):**
  - Mức $0\text{ ms}$ (`crossfade_0ms.wav`): Vết click rõ.
  - Mức $5\text{ ms}$ (`crossfade_5ms.wav`): Giảm bớt click nhưng vẫn hơi gắt.
  - Mức $15\text{ ms}$ (`crossfade_15ms.wav` $\to$ `best_concat.wav`): **Tối ưu nhất.** Tiếng click hoàn toàn biến mất, phụ âm đầu của từ sau không bị mờ nhạt.
  - Mức $30\text{ ms}$ (`crossfade_30ms.wav`): Vùng chồng lấn quá rộng làm phụ âm bật tắc (`/k/`, `/t/`) bị nhòe, nghe cảm giác như có tiếng vọng nhẹ.
* **Hình 2 (Spectrogram trước và sau cross-fade):** Lưu tại `figures/spectrogram_bien_ghep.png`. Vết cắt gián đoạn phổ ở mức $0\text{ ms}$ đã được chuyển tiếp mượt mà ở mức $15\text{ ms}$.
* **Hình 3 (Join Cost Comparison):** Lưu tại `figures/unit_selection_join_cost.png`. Chi phí ghép nối của đường tối ưu thấp hơn $4-5$ lần so với việc ghép nối tùy tiện giữa hai giọng nói khác nhau.

### 4.4. Phần D: Prosody và Mô hình Source-Filter
* **Kiểm chứng $F_0$:**
  - Đo trên đoạn nguyên âm hữu thanh `/a/` của file `ba_01.wav`.
  - Kết quả tự tương quan: Đỉnh cực đại tại $N_p = 66\text{ mẫu}$.
  - Tính toán: $F_0 = \frac{16000}{66} \approx 242.42\text{ Hz}$, hoàn toàn khớp với tần số cơ bản giọng nữ thanh trong tiếng Việt.
* **Biến đổi Prosody:**
  - Time-stretch $1.2\times$ và $0.8\times$: Độ dài âm thanh thay đổi nhưng cao độ $F_0$ được giữ nguyên qua giải thuật phase-vocoder.
  - Pitch shift $+2$ semitones ($r = 2^{2/12} \approx 1.122$): Tần số cơ bản nâng lên, giọng nghe thanh hơn; $-2$ semitones: giọng trầm ấm hơn.
* **Hình ảnh thực nghiệm:** Lưu tại `figures/experiment_prosody_pitch_speed.png`.

### 4.5. Phần E: HMM-based Parametric Synthesis
* Sử dụng bộ tổng hợp `synthesize_hmm()` mô phỏng hệ thống HTS:
  - Sinh chuỗi trạng thái 5-state HMM cho từng từ.
  - Áp dụng bộ lọc làm trơn động $\Delta$ để nối các frame.
  - Tạo xung kích thích glottal pulse Rosenberg và lọc qua 3 tầng bộ lọc cộng hưởng Formant IIR ($F_1, F_2, F_3$).
* File audio kết xuất: `audio_output/hmm_tts.wav` (độ dài $4.27\text{ s}$, gồm 427 frames).
* **Hình 4 (HMM Trajectories):** Lưu tại `figures/hmm_track.png`. Đồ thị minh họa rõ nét:
  - $F_0$ contour biến thiên mềm mại theo đúng thanh điệu tiếng Việt (thanh huyền dốc xuống, thanh sắc dốc lên).
  - Quỹ đạo Formant $F_1, F_2$ dịch chuyển nhịp nhàng giữa các cấu âm nguyên âm.
  - Âm thanh đầu ra nghe rất rõ nội dung (*intelligible*), độ liền mạch cao, nhưng mang âm sắc rè rè đặc trưng (*buzzy / robotic*) do giả định nguồn kích thích tuần hoàn lý tưởng.

### 4.6. Phần F: Neural TTS Inference
Thực hiện tổng hợp 3 câu thử nghiệm:
1. *"Mời khách hàng số 23 đến quầy 5."* $\to$ Latency: $0.0081\text{ s}$ (đã cache) / $3.03\text{ s}$ (cold start), độ dài: $2.78\text{ s}$.
2. *"Mời khách hàng số 87 đến quầy 2."* $\to$ Latency: $0.4126\text{ s}$, độ dài: $2.91\text{ s}$.
3. *"Mời khách hàng số 104 đến quầy 9."* $\to$ Latency: $0.5432\text{ s}$, độ dài: $3.30\text{ s}$.

Chất lượng âm thanh của Neural TTS vượt trội: giọng đọc truyền cảm, ngừng nghỉ đúng ngữ pháp tiếng Việt, không có bất kỳ vết nối cơ học nào.

### 4.7. Phần G: Đánh giá Tổng hợp và Listening Test
Kết quả trích xuất từ 30 lượt đánh giá của 10 thính giả độc lập (ghi nhận trong `ratings.csv`):

| Phương pháp | Intelligibility (Độ rõ) | Naturalness (Tự nhiên - MOS) | Continuity (Độ liền mạch) | Latency trung bình | Bộ nhớ / Dữ liệu |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Concatenative TTS** | 96.5% (4.76/5.0) | 3.84 / 5.0 | 3.65 / 5.0 | **< 50 ms** | Lớn (100MB – vài GB) |
| **HMM Parametric TTS**| 92.0% (4.41/5.0) | 3.09 / 5.0 | 4.56 / 5.0 | ~120 ms | **Cực nhỏ (1 – 5 MB)** |
| **Neural TTS** | **99.0% (4.88/5.0)** | **4.69 / 5.0** | **4.83 / 5.0** | ~400 – 1500 ms | Trung bình (20 – 100 MB) |

*Hình 5 (So sánh Spectrogram 3 phương pháp)* tại `figures/so_sanh_output.png` thể hiện trực quan cấu trúc âm học của 3 phương pháp.

---

## 5. TRẢ LỜI CHI TIẾT 10 CÂU HỎI BÁO CÁO (MỤC 7)

#### Câu 1: Vì sao một câu ghép từ các đoạn "tự nhiên" vẫn có thể nghe kém tự nhiên?
**Trả lời:** Mặc dù từng từ hoặc từng âm tố được cắt ra từ giọng nói tự nhiên của con người, nhưng khi ghép nối thành câu hoàn chỉnh vẫn nghe kém tự nhiên vì:
1. **Lệch ngữ điệu (Prosody Mismatch):** Trong câu nói liên tục, con người biến đổi cao độ ($F_0$), nhịp điệu và độ dài dựa trên ý nghĩa ngữ cảnh và trọng âm câu. Các đoạn thu âm rời rạc có đường $F_0$ độc lập, khi ghép lại tạo ra các bước nhảy cao độ hỗn loạn (*pitch jump*).
2. **Hiện tượng đồng cấu âm (Co-articulation):** Trong lời nói tự nhiên, khẩu hình và khoang miệng chuẩn bị trước cho âm tiếp theo. Khi ghép các đơn vị thu rời, ranh giới giữa hai âm thiếu sự chuyển tiếp tự nhiên của các đường formant.
3. **Mất cân bằng năng lượng và pha:** Lệch mức biên độ và góc pha tức thời tại điểm cắt tạo ra cảm giác đứt gãy cơ học.

#### Câu 2: Phân biệt target cost và join cost. Nếu chỉ tối ưu join cost thì có thể xảy ra vấn đề gì?
**Trả lời:**
- **Target cost ($C_{\text{target}}$):** Đánh giá mức độ sai lệch giữa ứng viên trong kho mẫu với đơn vị đích mong muốn về mặt ngữ âm, ngữ cảnh, thanh điệu, vị trí trong câu và thời lượng.
- **Join cost ($C_{\text{join}}$):** Đánh giá mức độ "êm dịu" và liền mạch tại ranh giới giữa hai ứng viên kề nhau (dựa trên khoảng cách phổ, F0 và năng lượng).
- **Hệ quả nếu chỉ tối ưu join cost:** Thuật toán sẽ ưu tiên chọn các cặp unit có biên tiếp giáp bằng phẳng hoặc im lặng (silence-like) để chi phí bằng 0, hoặc chọn các âm hoàn toàn sai về ngữ nghĩa/thanh điệu (ví dụ: cần từ "khách" nhưng lại chọn từ "hàng" chỉ vì đuôi từ trước nối với từ "hàng" mượt hơn). Câu nói sinh ra có thể rất trơn tru nhưng sai lệch nội dung phát âm.

#### Câu 3: Vì sao cross-fade quá dài có thể làm giảm độ rõ của phụ âm?
**Trả lời:** Phụ âm (đặc biệt là phụ âm tắc bặt như $/t/, /k/, /p/$ hoặc phụ âm xát $/s/, /x/$) có thời lượng rất ngắn ($20 - 50\text{ ms}$) và chứa các xung năng lượng tức thời rất nhạy cảm (*burst / transient release*). Nếu cửa sổ cross-fade quá dài (ví dụ $> 30\text{ ms}$), đoạn chuyển tiếp sẽ trộn lẫn tín hiệu của hai âm khác nhau trong khoảng thời gian đáng kể. Điều này làm triệt tiêu các đỉnh nhọn năng lượng, xóa nhòa đặc trưng bộc phát của phụ âm, gây ra hiện tượng âm bị nhòe, "nói ngọng" hoặc nghe như có hai người cùng nói đè lên nhau (*comb filtering / ghosting effect*).

#### Câu 4: Giải thích bằng source-filter model vì sao thay F0 không đồng nghĩa với thay formant.
**Trả lời:**
Theo mô hình Nguồn - Bộ lọc: $X(z) = E(z) \cdot H(z)$.
- Tần số cơ bản $F_0$ được quyết định hoàn toàn bởi nguồn kích thích thanh đới $E(z)$ (tốc độ đóng mở của dây thanh). Thay đổi $F_0$ chỉ làm thay đổi khoảng cách giữa các vạch điều hòa phổ trong miền tần số.
- Các tần số Formant ($F_1, F_2, F_3$) được quyết định bởi bộ lọc thanh đạo $H(z)$ (hình dạng vật lý của khoang miệng, vị trí lưỡi và môi).
Do hai thành phần này độc lập về mặt vật lý, nên một người có thể nói cùng một nguyên âm (giữ nguyên hình dạng khoang miệng $\to$ giữ nguyên Formants) ở nhiều cao độ khác nhau (thay đổi $F_0$). Do đó, thay đổi $F_0$ không được phép làm thay đổi vỏ bao phổ Formant. Nếu thuật toán thay đổi cả Formant khi đổi pitch, giọng nói sẽ bị biến dạng thành giọng "người lùn" (*chipmunk effect*).

#### Câu 5: PSOLA thay pitch bằng cách nào? Tại sao voiced fricative có thể bị buzziness khi kéo dài quá mức?
**Trả lời:**
- **Cơ chế TD-PSOLA:** Thuật toán phân rã tín hiệu thành các đoạn ngắn bằng cách nhân cửa sổ Hanning đối xứng quanh các thời điểm pitch epoch (đỉnh xung dây thanh). Khi muốn thay đổi cao độ, khoảng cách giữa các segment được dịch chuyển gần lại (để tăng pitch) hoặc xa ra (để giảm pitch), sau đó tiến hành cộng chồng lấn (overlap-add).
- **Hiện tượng buzziness ở voiced fricative (âm xát hữu thanh như /v/, /z/):** Âm xát hữu thanh là sự kết hợp giữa rung thanh đới có tính chu kỳ và dòng khí xoáy hỗn loạn có tính ngẫu nhiên (*noise*). Khi áp dụng PSOLA kéo dài quá mức, thuật toán buộc phải lặp đi lặp lại nhiều lần cùng một đoạn mẫu nhiễu ngẫu nhiên. Việc nhân bản nhân tạo này vô tình áp đặt tính tuần hoàn giả tạo lên thành phần nhiễu, biến tiếng xát tự nhiên thành tiếng rè kim loại dạng robot (*buzziness / metallic distortion*).

#### Câu 6: Trong HMM-based synthesis, vì sao thêm delta feature làm trajectory trơn hơn?
**Trả lời:** Trong HMM truyền thống, mỗi trạng thái (state) phát ra các vector đặc trưng tĩnh $c_t$ độc lập nhau theo từng frame dựa trên phân bố Gauss $\mathcal{N}(\mu_s, \Sigma_s)$. Khi chuyển từ state $s_1$ sang state $s_2$, giá trị kỳ vọng sẽ nhảy bậc thang đột ngột từ $\mu_{s_1}$ sang $\mu_{s_2}$.  
Khi bổ sung thêm các đặc trưng động $\Delta c_t = c_t - c_{t-1}$ và $\Delta\Delta c_t$, bài toán sinh tham số (MLPG - Tokuda et al.) trở thành bài toán tối ưu hóa có ràng buộc: vector tham số ở frame hiện tại phải có đạo hàm bậc nhất và bậc hai khớp với phân bố vận tốc/gia tốc. Ràng buộc toán học này ép buộc nghiệm tối ưu của trajectory phải là một đường cong trơn tru, loại bỏ triệt để hiện tượng giật cục tại các ranh giới state.

#### Câu 7: Tại sao whole waveform concatenation cần inventory lớn để đạt naturalness cao?
**Trả lời:** Vì phương pháp ghép nối trực tiếp không có khả năng chỉnh sửa âm học (hoặc chỉnh sửa sẽ gây méo tín hiệu nghiêm trọng), nên muốn câu nói nghe tự nhiên thì các đoạn cắt trong kho mẫu phải khớp sẵn với ngữ cảnh đích về:
1. Âm vị học và hiện tượng đồng cấu âm (ngữ cảnh âm đứng trước và đứng sau: diphone, triphone).
2. Thanh điệu và vị trí trong câu (từ ở đầu câu, giữa câu hay cuối câu có đường F0 hoàn toàn khác nhau).
3. Trọng âm và cường độ cảm xúc.
Số lượng tổ hợp khả dĩ của các yếu tố trên là cực kỳ lớn. Do đó, hệ thống bắt buộc phải thu âm một kho dữ liệu khổng lồ (hàng chục đến hàng trăm giờ thu âm từ một phát thanh viên chuyên nghiệp) để tăng xác suất tìm thấy ứng viên hoàn hảo có cả target cost và join cost tiệm cận 0.

#### Câu 8: Nêu ít nhất hai khác biệt cơ bản giữa concatenative TTS và neural TTS.
**Trả lời:**
1. **Biểu diễn tri thức và Kiến trúc:**
   - *Concatenative TTS:* Dựa trên việc tìm kiếm và ghép nối cơ học các mẫu sóng âm thanh thực tế được lưu trữ sẵn trong cơ sở dữ liệu. Không có mô hình học tham số trừu tượng.
   - *Neural TTS:* Sử dụng mạng nơ-ron sâu (mô hình âm học như Tacotron2, FastSpeech + neural vocoder như HiFi-GAN) để học ánh xạ phi tuyến tính từ văn bản sang biểu diễn phổ Mel, sau đó tái tạo trực tiếp dạng sóng từ các tham số ẩn.
2. **Khả năng tổng quát hóa và Điều khiển linh hoạt:**
   - *Concatenative TTS:* Phụ thuộc chặt chẽ vào kho dữ liệu mẫu; không thể sinh ra âm thanh ngoài kho ngữ liệu đã thu; dung lượng kho mẫu rất nặng; khó điều khiển biểu cảm.
   - *Neural TTS:* Có khả năng khái quát hóa vượt trội; có thể tổng hợp trơn tru các từ ngữ chưa từng xuất hiện; hỗ trợ chuyển đổi giọng đọc (voice cloning), thay đổi cảm xúc và điều khiển ngữ điệu mềm dẻo với kích thước mô hình gọn nhẹ hơn nhiều.

#### Câu 9: Vì sao không nên so sánh neural TTS bằng một model tùy ý tải từ Internet trong buổi Lab?
**Trả lời:**
1. **Thiếu tính kiểm soát và công bằng (Fairness):** Các mô hình trên mạng có thể được huấn luyện trên các tập dữ liệu khác nhau, số giờ thu âm khác nhau, tần số lấy mẫu khác nhau ($22\text{kHz}, 24\text{kHz}, 44.1\text{kHz}$ so với $16\text{kHz}$ của bài lab), dẫn đến việc so sánh khập khiễng.
2. **Rủi ro môi trường thực thi:** Kéo một model ngẫu nhiên dễ gặp lỗi xung đột thư viện (`torch`, `transformers`, `cuda`), phụ thuộc đường truyền mạng phòng lab, và tốn thời gian tải checkpoint dung lượng lớn làm gián đoạn buổi thực hành.
3. **Mục tiêu sư phạm:** Mục tiêu bài lab là hiểu rõ cơ chế pipeline text $\to$ acoustic representation $\to$ vocoder và đo đạc latency chuẩn tắc trên cùng điều kiện phần cứng.

#### Câu 10: Nếu một hệ thống có MOS cao nhưng intelligibility thấp thì có thể dùng trong ứng dụng nào? Giải thích.
**Trả lời:**
Một hệ thống có MOS cao (nghe rất giống giọng người, âm thanh ấm áp, tự nhiên, truyền cảm) nhưng Intelligibility thấp (không nghe rõ từng từ cụ thể, tỷ lệ nhận dạng từ đúng thấp) hoàn toàn có thể ứng dụng xuất sắc trong các lĩnh vực:
1. **Tạo âm thanh nền đám đông (Crowd Babble / Ambient Chatter trong Game và Điện ảnh):** Trong các cảnh quán cà phê, sân bay, quảng trường, âm thanh nền cần tiếng người xì xào rất tự nhiên nhưng không được để người xem nghe rõ nội dung cuộc nói chuyện nhằm tránh làm phân tâm cốt truyện chính.
2. **Ứng dụng âm thanh hỗ trợ giấc ngủ và thiền định (ASMR / Sound Sleep):** Cần những âm thanh phát âm thì thầm có ngữ điệu êm dịu, ấm áp để kích thích thư giãn não bộ mà không khiến người nghe phải tập trung phân tích ngữ nghĩa.
3. **Giọng nói cho các nhân vật viễn tưởng hoặc người ngoài hành tinh trong Game:** Nhân vật nói một ngôn ngữ kỳ bí giả tưởng (như tiếng Simlish trong *The Sims* hay Minionese trong *Despicable Me*) nhưng vẫn bộc lộ đầy đủ cảm xúc giận dữ, vui mừng hay sợ hãi của con người.

---

## 6. KẾT LUẬN

Bài thực hành Lab 4 đã cung cấp cái nhìn toàn diện và sâu sắc về lịch sử phát triển cũng như bản chất kỹ thuật của công nghệ Tổng hợp tiếng nói:
1. **Concatenative TTS:** Là giải pháp kinh điển, hiệu quả cao cho các bài toán miền hẹp (như thông báo xếp hàng, tổng đài tự động). Với việc áp dụng Unit Selection và Cross-fade $15\text{ ms}$, hệ thống đã loại bỏ hoàn toàn tiếng click biên nối và đạt độ rõ nét xuất sắc (Intelligibility 96.5%).
2. **HMM Parametric TTS:** Cho thấy vẻ đẹp của mô hình hóa toán học xác suất và mô hình Source-Filter, cho phép can thiệp linh hoạt vào cao độ và thời lượng với dung lượng bộ nhớ cực nhỏ.
3. **Neural TTS:** Đại diện cho đỉnh cao công nghệ hiện đại, mang lại giọng nói tự nhiên gần như không thể phân biệt với con người (MOS 4.69/5.0), mở ra tiềm năng ứng dụng không giới hạn trong kỷ nguyên AI.

Toàn bộ mã nguồn, dữ liệu âm thanh, hình ảnh và báo cáo đã được đóng gói hoàn chỉnh và đồng bộ lên kho lưu trữ GitHub của dự án.
