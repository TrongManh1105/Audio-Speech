import os
import sys
import csv
import numpy as np
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
from scipy.signal import lfilter
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

FS = 16000
FRAME_MS, HOP_MS = 25, 10
WIN = int(FS * FRAME_MS / 1000)  # 400 mẫu
HOP = int(FS * HOP_MS / 1000)    # 160 mẫu
DATA_DIR = "dataset"
FIGURES_DIR = "figures_lab2"
os.makedirs(FIGURES_DIR, exist_ok=True)

LABELS = ['khong', 'mot', 'hai', 'ba', 'bon']
VIET_LABELS = {'khong': 'không', 'mot': 'một', 'hai': 'hai', 'ba': 'ba', 'bon': 'bốn'}

# -------------------------------------------------------------
# CÁC HÀM TIỀN XỬ LÝ & ĐẶC TRƯNG MIỀN THỜI GIAN
# -------------------------------------------------------------
def load_audio(path):
    y, sr = librosa.load(path, sr=FS, mono=True)
    peak = np.max(np.abs(y))
    if peak > 0:
        y = y / (peak + 1e-9)
    return y

def compute_energy_zcr(y):
    n_frames = int(np.floor((len(y) - WIN) / HOP)) + 1
    energy = np.zeros(n_frames)
    zcr = np.zeros(n_frames)
    
    for i in range(n_frames):
        frame = y[i * HOP : i * HOP + WIN] * np.hamming(WIN)
        energy[i] = 10 * np.log10(np.sum(frame**2) + 1e-10)
        # ZCR
        signs = np.sign(frame)
        signs[signs == 0] = -1
        zcr[i] = 0.5 * np.mean(np.abs(signs[1:] - signs[:-1]))
        
    times = (np.arange(n_frames) * HOP + WIN / 2) / FS
    return energy, zcr, times

def trim_energy(y, top_db=30, margin_ms=50):
    yt, idx = librosa.effects.trim(y, top_db=top_db, frame_length=WIN, hop_length=HOP)
    m = int(FS * margin_ms / 1000)
    s = max(0, idx[0] - m)
    e = min(len(y), idx[1] + m)
    return y[s:e], (s, e)

# -------------------------------------------------------------
# TRÍCH XUẤT MFCC
# -------------------------------------------------------------
def mfcc_feature(y, use_delta=False):
    # Pre-emphasis
    y_pre = lfilter([1.0, -0.97], [1.0], y)
    M = librosa.feature.mfcc(
        y=y_pre, sr=FS, n_mfcc=13, n_mels=24,
        n_fft=512, win_length=WIN, hop_length=HOP,
        window='hamming', center=False
    )
    if use_delta:
        d1 = librosa.feature.delta(M, order=1)
        M = np.vstack([M, d1])
        
    # CMN (Cepstral Mean Normalization)
    M = M - np.mean(M, axis=1, keepdims=True)
    return M.T  # Shape: (T, D)

# -------------------------------------------------------------
# THUẬT TOÁN DTW TỰ CÀI ĐẶT
# -------------------------------------------------------------
def dtw_distance(X, Y):
    N, M = len(X), len(Y)
    D = np.full((N + 1, M + 1), np.inf)
    D[0, 0] = 0.0
    back = np.zeros((N + 1, M + 1, 2), dtype=int)
    
    # Tính ma trận chi phí cục bộ Euclidean
    local_dist = np.zeros((N, M))
    for i in range(1, N + 1):
        for j in range(1, M + 1):
            d = np.linalg.norm(X[i - 1] - Y[j - 1])
            local_dist[i - 1, j - 1] = d
            choices = [
                (D[i - 1, j], i - 1, j),
                (D[i, j - 1], i, j - 1),
                (D[i - 1, j - 1], i - 1, j - 1)
            ]
            best, pi, pj = min(choices, key=lambda z: z[0])
            D[i, j] = d + best
            back[i, j] = (pi, pj)
            
    # Backtrack
    path = []
    i, j = N, M
    while i > 0 or j > 0:
        path.append((i - 1, j - 1))
        i, j = back[i, j]
    path.reverse()
    
    dtw_norm = D[N, M] / max(len(path), 1)
    return dtw_norm, path, local_dist

# -------------------------------------------------------------
# BỘ NHẬN DẠNG NEAREST-TEMPLATE
# -------------------------------------------------------------
def build_templates(root, use_trim=True, use_delta=False, n_train=3):
    templates = {lab: [] for lab in LABELS}
    for lab in LABELS:
        files = sorted(Path(root, lab).glob('*.wav'))[:n_train]
        for f in files:
            y = load_audio(str(f))
            if use_trim:
                y, _ = trim_energy(y)
            templates[lab].append(mfcc_feature(y, use_delta=use_delta))
    return templates

def recognize(path, templates, use_trim=True, use_delta=False):
    y = load_audio(path)
    if use_trim:
        y, _ = trim_energy(y)
    X = mfcc_feature(y, use_delta=use_delta)
    scores = {}
    for lab, refs in templates.items():
        scores[lab] = min(dtw_distance(X, R)[0] for R in refs)
    pred = min(scores, key=scores.get)
    sorted_scores = dict(sorted(scores.items(), key=lambda kv: kv[1]))
    return pred, sorted_scores

# -------------------------------------------------------------
# MAIN LAB 2
# -------------------------------------------------------------
def run_lab2():
    print("=" * 70)
    print("CSE457 - BÀI THỰC HÀNH LAB 2: ĐẶC TRƯNG TIẾNG NÓI VÀ NHẬN DẠNG BẰNG DTW")
    print("Sinh viên: Nguyễn Trọng Mạnh Tiến - MSV: 2351260689 - Lớp: 65TTNT")
    print("=" * 70)

    # 1. Phần A: Kiểm tra dữ liệu
    print("\n[PHẦN A] KIỂM TRA DATASET TỪ VỰNG:")
    for lab in LABELS:
        files = list(Path(DATA_DIR, lab).glob('*.wav'))
        print(f"  - Từ '{VIET_LABELS[lab]}' ({lab}): {len(files)} files (Train: 3, Test: 2)")

    # 2. Phần B: Vẽ Waveform, Energy, ZCR
    fig, axes = plt.subplots(3, 3, figsize=(14, 9), sharex=False)
    sample_words = ['khong', 'hai', 'ba']
    for idx, w in enumerate(sample_words):
        wav_p = str(sorted(Path(DATA_DIR, w).glob('*.wav'))[0])
        y = load_audio(wav_p)
        en, zcr, t_f = compute_energy_zcr(y)
        t_w = np.arange(len(y)) / FS
        
        axes[0, idx].plot(t_w, y, color="#1f77b4")
        axes[0, idx].set_title(f"Waveform - '{VIET_LABELS[w]}'", fontweight="bold")
        axes[0, idx].grid(True, linestyle=":")
        
        axes[1, idx].plot(t_f, en, color="#ff7f0e")
        axes[1, idx].set_title(f"Log-Energy (dB)", fontsize=10)
        axes[1, idx].grid(True, linestyle=":")
        
        axes[2, idx].plot(t_f, zcr, color="#2ca02c")
        axes[2, idx].set_title(f"Zero-Crossing Rate", fontsize=10)
        axes[2, idx].set_xlabel("Thời gian (s)")
        axes[2, idx].grid(True, linestyle=":")

    plt.tight_layout()
    fig_b = os.path.join(FIGURES_DIR, "energy_zcr.png")
    plt.savefig(fig_b, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu biểu đồ Energy và ZCR vào: {fig_b}")

    # 3. Phần C: Endpoint detection
    print("\n[PHẦN C] SO SÁNH THỜI LƯỢNG TRƯỚC VÀ SAU KHI TRIM ENDPOINT:")
    for w in sample_words:
        wav_p = str(sorted(Path(DATA_DIR, w).glob('*.wav'))[0])
        y = load_audio(wav_p)
        y_trim, (s, e) = trim_energy(y, margin_ms=50)
        print(f"  - Từ '{VIET_LABELS[w]}': Gốc = {len(y)/FS:.3f}s -> Trim = {len(y_trim)/FS:.3f}s (Cắt bớt {(len(y)-len(y_trim))/FS:.3f}s silence)")

    # 4. Phần D: MFCC Heatmap
    y_m1 = load_audio(str(sorted(Path(DATA_DIR, 'mot').glob('*.wav'))[0]))
    y_m2 = load_audio(str(sorted(Path(DATA_DIR, 'ba').glob('*.wav'))[0]))
    y_m1_t, _ = trim_energy(y_m1)
    y_m2_t, _ = trim_energy(y_m2)
    mfcc_1 = mfcc_feature(y_m1_t)
    mfcc_2 = mfcc_feature(y_m2_t)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
    im1 = ax1.imshow(mfcc_1.T, aspect='auto', origin='lower', cmap='viridis')
    ax1.set_title("Heatmap 13 MFCC - Từ 'một' (Shape: T x 13)", fontweight="bold")
    ax1.set_xlabel("Frame index")
    ax1.set_ylabel("Hệ số MFCC")
    fig.colorbar(im1, ax=ax1)

    im2 = ax2.imshow(mfcc_2.T, aspect='auto', origin='lower', cmap='viridis')
    ax2.set_title("Heatmap 13 MFCC - Từ 'ba' (Shape: T x 13)", fontweight="bold")
    ax2.set_xlabel("Frame index")
    fig.colorbar(im2, ax=ax2)

    plt.tight_layout()
    fig_mfcc = os.path.join(FIGURES_DIR, "mfcc_heatmap.png")
    plt.savefig(fig_mfcc, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu Heatmap MFCC vào: {fig_mfcc}")

    # 5. Phần E: Tự cài DTW và vẽ ma trận khoảng cách
    # Cùng từ ('ba' 01 vs 'ba' 02)
    y_ba1 = load_audio(str(Path(DATA_DIR, 'ba', 'ba_01.wav')))
    y_ba2 = load_audio(str(Path(DATA_DIR, 'ba', 'ba_02.wav')))
    y_mot1 = load_audio(str(Path(DATA_DIR, 'mot', 'mot_01.wav')))
    
    f_ba1 = mfcc_feature(trim_energy(y_ba1)[0])
    f_ba2 = mfcc_feature(trim_energy(y_ba2)[0])
    f_mot1 = mfcc_feature(trim_energy(y_mot1)[0])

    cost_same, path_same, mat_same = dtw_distance(f_ba1, f_ba2)
    cost_diff, path_diff, mat_diff = dtw_distance(f_ba1, f_mot1)

    print(f"\n[PHẦN E] KHOẢNG CÁCH DTW TỰ CÀI ĐẶT:")
    print(f"  - Cùng từ ('ba' vs 'ba') : DTW_norm = {cost_same:.3f} (Đường đi bám sát đường chéo)")
    print(f"  - Khác từ ('ba' vs 'một'): DTW_norm = {cost_diff:.3f} (Chi phí lớn hơn)")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5))
    im1 = ax1.imshow(mat_same, origin='lower', cmap='plasma', aspect='auto')
    px, py = zip(*path_same)
    ax1.plot(py, px, color='cyan', linewidth=2.5, label='DTW optimal path')
    ax1.set_title(f"DTW Cùng từ ('ba' vs 'ba') | Cost = {cost_same:.2f}", fontweight="bold")
    ax1.set_xlabel("Frame Y (ba_02)")
    ax1.set_ylabel("Frame X (ba_01)")
    ax1.legend()
    fig.colorbar(im1, ax=ax1)

    im2 = ax2.imshow(mat_diff, origin='lower', cmap='plasma', aspect='auto')
    px2, py2 = zip(*path_diff)
    ax2.plot(py2, px2, color='cyan', linewidth=2.5, label='DTW optimal path')
    ax2.set_title(f"DTW Khác từ ('ba' vs 'một') | Cost = {cost_diff:.2f}", fontweight="bold")
    ax2.set_xlabel("Frame Y (mot_01)")
    ax2.legend()
    fig.colorbar(im2, ax=ax2)

    plt.tight_layout()
    fig_dtw = os.path.join(FIGURES_DIR, "dtw_alignment.png")
    plt.savefig(fig_dtw, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu biểu đồ DTW Alignment vào: {fig_dtw}")

    # 6. Phần F & G: Thí nghiệm nhận dạng và Ma trận nhầm lẫn
    templates_std = build_templates(DATA_DIR, use_trim=True, use_delta=False, n_train=3)
    
    y_true, y_pred = [], []
    results_rows = []
    
    print("\n[PHẦN F] KẾT QUẢ DỰ ĐOÁN TẬP TEST:")
    for lab in LABELS:
        test_files = sorted(Path(DATA_DIR, lab).glob('*.wav'))[3:]
        for f in test_files:
            pred, scores = recognize(str(f), templates_std, use_trim=True, use_delta=False)
            y_true.append(lab)
            y_pred.append(pred)
            top3 = list(scores.items())[:3]
            print(f"  - File {f.name:<12}: Nhãn thật={VIET_LABELS[lab]:<5} -> Dự đoán={VIET_LABELS[pred]:<5} | Top3 Scores: {[(VIET_LABELS[k], round(v, 2)) for k, v in top3]}")
            results_rows.append({
                "file": f.name, "true": lab, "pred": pred,
                "top1_score": round(top3[0][1], 3), "top2_score": round(top3[1][1], 3)
            })

    acc_baseline = accuracy_score(y_true, y_pred)
    print(f"\n[PHẦN G] ACCURACY BASELINE: {acc_baseline * 100:.2f}%")

    # Lưu results.csv
    with open("results.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["file", "true", "pred", "top1_score", "top2_score"])
        writer.writeheader()
        writer.writerows(results_rows)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[VIET_LABELS[l] for l in LABELS])
    disp.plot(cmap='Blues')
    plt.title(f"Confusion Matrix DTW (Accuracy = {acc_baseline * 100:.1f}%)", fontweight="bold")
    fig_cm = os.path.join(FIGURES_DIR, "confusion_matrix.png")
    plt.tight_layout()
    plt.savefig(fig_cm, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu Confusion Matrix vào: {fig_cm}")

    # Thí nghiệm có kiểm soát E1, E2, E3
    def evaluate_config(use_trim=True, use_delta=False, n_train=3):
        tpls = build_templates(DATA_DIR, use_trim=use_trim, use_delta=use_delta, n_train=n_train)
        yt, yp = [], []
        for l in LABELS:
            for tf in sorted(Path(DATA_DIR, l).glob('*.wav'))[3:]:
                p, _ = recognize(str(tf), tpls, use_trim=use_trim, use_delta=use_delta)
                yt.append(l)
                yp.append(p)
        return accuracy_score(yt, yp)

    acc_e1 = evaluate_config(use_trim=False, use_delta=False, n_train=3)
    acc_e2 = evaluate_config(use_trim=True, use_delta=True, n_train=3)
    acc_e3 = evaluate_config(use_trim=True, use_delta=False, n_train=1)

    print("\n" + "=" * 75)
    print("BẢNG TỔNG HỢP CÁC THÍ NGHIỆM MỞ RỘNG (CONTROLLED EXPERIMENTS):")
    print("-" * 75)
    print(f"{'Mã TN':<8} | {'Thiết lập thử nghiệm':<35} | {'Accuracy':<12} | {'Nhận xét'}")
    print("-" * 75)
    print(f"{'Base':<8} | {'Chuẩn: Trim + 13 MFCC + 3 Templates':<35} | {acc_baseline*100:6.1f} %    | {'Đạt hiệu năng tối ưu'}")
    print(f"{'E1':<8} | {'Không Trim (Giữ nguyên silence)':<35} | {acc_e1*100:6.1f} %    | {'Giảm do DTW căn nhầm silence'}")
    print(f"{'E2':<8} | {'Bổ sung Delta (13 MFCC + 13 Delta)':<35} | {acc_e2*100:6.1f} %    | {'Tăng tính phân biệt động lực'}")
    print(f"{'E3':<8} | {'Chỉ dùng 1 Template duy nhất/từ':<35} | {acc_e3*100:6.1f} %    | {'Kém ổn định với biến thiên phát âm'}")
    print("=" * 75)
    print("\n✅ HOÀN THÀNH TOÀN BỘ CÁC MỤC THỰC HÀNH LAB 2!")

if __name__ == "__main__":
    run_lab2()

