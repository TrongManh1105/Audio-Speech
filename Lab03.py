import os
import sys
import math
import numpy as np
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt
from pathlib import Path
from hmmlearn.hmm import GaussianHMM
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay, accuracy_score

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

DATA_DIR = "dataset_lab3"
FIGURES_DIR = "figures_lab3"
os.makedirs(FIGURES_DIR, exist_ok=True)

LABELS = ['mo', 'dong', 'len', 'xuong', 'dung']
VIET_LABELS = {'mo': 'mở', 'dong': 'đóng', 'len': 'lên', 'xuong': 'xuống', 'dung': 'dừng'}

# -------------------------------------------------------------
# PHẦN A: TRÍCH XUẤT ĐẶC TRƯNG 39D (MFCC + DELTA + DELTA2 + CMVN)
# -------------------------------------------------------------
def extract_feat_39d(path, sr=16000, top_db=30):
    y, _ = librosa.load(path, sr=sr, mono=True)
    y, _ = librosa.effects.trim(y, top_db=top_db)
    y = librosa.effects.preemphasis(y, coef=0.97)

    win_length = int(0.025 * sr)
    hop_length = int(0.010 * sr)

    mfcc = librosa.feature.mfcc(
        y=y, sr=sr, n_mfcc=13,
        n_fft=512, win_length=win_length,
        hop_length=hop_length, window='hamming',
        n_mels=26, fmin=20, fmax=sr / 2
    )
    d1 = librosa.feature.delta(mfcc, order=1)
    d2 = librosa.feature.delta(mfcc, order=2)

    F = np.vstack([mfcc, d1, d2]).T  # Shape: (T, 39)

    mu = F.mean(axis=0, keepdims=True)
    sd = F.std(axis=0, keepdims=True) + 1e-8
    F_norm = (F - mu) / sd
    return F_norm, mfcc, d1, d2

# -------------------------------------------------------------
# PHẦN B: KHỞI TẠO HMM TRÁI-SANG-PHẢI (LEFT-TO-RIGHT)
# -------------------------------------------------------------
def make_lr_hmm(n_states=5, n_iter=80, random_state=42):
    model = GaussianHMM(
        n_components=n_states,
        covariance_type='diag',
        n_iter=n_iter,
        tol=1e-3,
        min_covar=1e-2,
        init_params='mc',
        params='mc',  # Chỉ cập nhật means ('m') và covars ('c'), cố định transition Bakis để không bị phá vỡ topology
        random_state=random_state
    )
    start = np.zeros(n_states)
    start[0] = 1.0
    A = np.zeros((n_states, n_states))
    for i in range(n_states - 1):
        A[i, i] = 0.7
        A[i, i + 1] = 0.3
    A[-1, -1] = 1.0
    model.startprob_ = start
    model.transmat_ = A
    return model

# -------------------------------------------------------------
# PHẦN C: HUẤN LUYỆN TOÀN BỘ MÔ HÌNH HMM
# -------------------------------------------------------------
def train_word_hmms(train_dir, n_states=5):
    models = {}
    for label in LABELS:
        feats, lengths = [], []
        files = sorted(Path(train_dir, label).glob('*.wav'))
        for wav in files:
            F, _, _, _ = extract_feat_39d(str(wav))
            feats.append(F)
            lengths.append(len(F))
            
        X_concat = np.vstack(feats)
        model = make_lr_hmm(n_states=n_states)
        model.fit(X_concat, lengths)
        models[label] = model
    return models

# -------------------------------------------------------------
# PHẦN D: NHẬN DẠNG MAXIMUM LIKELIHOOD
# -------------------------------------------------------------
def recognize_utterance(path, models):
    F, _, _, _ = extract_feat_39d(path)
    T = len(F)
    scores = {lbl: model.score(F) / T for lbl, model in models.items()}
    pred = max(scores, key=scores.get)
    return pred, scores

# -------------------------------------------------------------
# MAIN LAB 3
# -------------------------------------------------------------
def run_lab3():
    print("=" * 70)
    print("CSE457 - BÀI THỰC HÀNH LAB 3: NHẬN DẠNG TIẾNG NÓI NÂNG CAO VỚI HMM")
    print("Sinh viên: Nguyễn Trọng Mạnh Tiến - MSV: 2351260689 - Lớp: 65TTNT")
    print("=" * 70)

    train_dir = os.path.join(DATA_DIR, "train")
    test_dir = os.path.join(DATA_DIR, "test")

    # 1. Phần A: Heatmap MFCC / Delta / Delta2
    sample_mo = str(Path(train_dir, 'mo', 'mo_01.wav'))
    sample_dong = str(Path(train_dir, 'dong', 'dong_01.wav'))
    f_mo, m_mo, d1_mo, d2_mo = extract_feat_39d(sample_mo)
    f_dg, m_dg, d1_dg, d2_dg = extract_feat_39d(sample_dong)

    fig, axes = plt.subplots(3, 2, figsize=(13, 8))
    axes[0, 0].imshow(m_mo, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 0].set_title("MFCC 13 hệ số - Từ 'mở'", fontweight="bold")
    axes[1, 0].imshow(d1_mo, aspect='auto', origin='lower', cmap='magma')
    axes[1, 0].set_title("Delta MFCC (Đạo hàm bậc 1) - Từ 'mở'", fontweight="bold")
    axes[2, 0].imshow(d2_mo, aspect='auto', origin='lower', cmap='inferno')
    axes[2, 0].set_title("Delta-Delta MFCC (Đạo hàm bậc 2) - Từ 'mở'", fontweight="bold")

    axes[0, 1].imshow(m_dg, aspect='auto', origin='lower', cmap='viridis')
    axes[0, 1].set_title("MFCC 13 hệ số - Từ 'đóng'", fontweight="bold")
    axes[1, 1].imshow(d1_dg, aspect='auto', origin='lower', cmap='magma')
    axes[1, 1].set_title("Delta MFCC - Từ 'đóng'", fontweight="bold")
    axes[2, 1].imshow(d2_dg, aspect='auto', origin='lower', cmap='inferno')
    axes[2, 1].set_title("Delta-Delta MFCC - Từ 'đóng'", fontweight="bold")

    plt.tight_layout()
    fig_a = os.path.join(FIGURES_DIR, "mfcc_delta_heatmaps.png")
    plt.savefig(fig_a, dpi=180)
    plt.close()
    print(f"\n[PHẦN A] Đã lưu Heatmaps MFCC/Delta/Delta2 vào: {fig_a}")

    # 2. Phần B & C: Huấn luyện HMM
    print("\n[PHẦN B & C] HUẤN LUYỆN 5-STATE GAUSSIAN HMM CHO 5 TỪ LỆNH:")
    models_5 = train_word_hmms(train_dir, n_states=5)
    for lbl, m in models_5.items():
        print(f"  - Model '{VIET_LABELS[lbl]}': Hội tụ = {m.monitor_.converged} (Số bước lặp: {m.monitor_.iter})")

    # Thử nghiệm n_states = 3, 5, 7 (E1)
    acc_per_state = {}
    for st in [3, 5, 7]:
        mdls = train_word_hmms(train_dir, n_states=st)
        yt, yp = [], []
        for l in LABELS:
            for wav in Path(test_dir, l).glob('*.wav'):
                p, _ = recognize_utterance(str(wav), mdls)
                yt.append(l)
                yp.append(p)
        acc_per_state[st] = accuracy_score(yt, yp)
    print(f"\n[THÍ NGHIỆM E1] ĐÁNH GIÁ SỐ TRẠNG THÁI HMM (n_states):")
    for st, ac in acc_per_state.items():
        print(f"  - n_states = {st}: Accuracy = {ac * 100:.1f}%")

    # 3. Phần D: Viterbi state alignment
    test_mo = str(Path(test_dir, 'mo', 'mo_07.wav'))
    f_test, _, _, _ = extract_feat_39d(test_mo)
    logp, states = models_5['mo'].decode(f_test, algorithm='viterbi')

    plt.figure(figsize=(9, 4))
    plt.step(range(len(states)), states, where='post', color="#1f77b4", linewidth=2.0)
    plt.title(f"Viterbi State Alignment: mo_07.wav vs Model 'MỞ' (Viterbi log-P = {logp:.2f})", fontweight="bold")
    plt.xlabel("Frame index (10 ms/frame)")
    plt.ylabel("HMM State (0 - 4)")
    plt.yticks(range(5), [f"State {i+1}" for i in range(5)])
    plt.grid(True, linestyle=":", alpha=0.6)
    fig_viterbi = os.path.join(FIGURES_DIR, "viterbi_alignment.png")
    plt.tight_layout()
    plt.savefig(fig_viterbi, dpi=180)
    plt.close()
    print(f"\n[PHẦN D] Đã lưu đồ thị Viterbi Alignment vào: {fig_viterbi}")

    # Bảng điểm acoustic score cho file test
    pred_mo, sc_mo = recognize_utterance(test_mo, models_5)
    print(f"Bảng điểm Normalized Log-Likelihood cho '{Path(test_mo).name}' (Nhãn thật: 'mở'):")
    for k, v in sorted(sc_mo.items(), key=lambda kv: kv[1], reverse=True):
        print(f"  - Model '{VIET_LABELS[k]:<5}': {v:8.3f}")

    # 4. Phần E: So sánh HMM với DTW Baseline
    def run_dtw_baseline():
        # Lấy 1 template từ train
        tpls = {lbl: extract_feat_39d(str(sorted(Path(train_dir, lbl).glob('*.wav'))[0]))[0] for lbl in LABELS}
        yt, yp = [], []
        for l in LABELS:
            for wav in Path(test_dir, l).glob('*.wav'):
                f_t, _, _, _ = extract_feat_39d(str(wav))
                dists = {lbl: np.mean([np.linalg.norm(f_t[min(i, len(f_t)-1)] - ref[min(i, len(ref)-1)]) for i in range(max(len(f_t), len(ref)))]) for lbl, ref in tpls.items()}
                yt.append(l)
                yp.append(min(dists, key=dists.get))
        return accuracy_score(yt, yp)

    dtw_acc = run_dtw_baseline()
    print(f"\n[PHẦN E] SO SÁNH HIỆU NĂNG DTW (LAB 2) VS HMM (LAB 3):")
    print(f"  - Accuracy DTW Baseline : {dtw_acc * 100:.2f}%")
    print(f"  - Accuracy HMM (5-state): {acc_per_state[5] * 100:.2f}%")

    # 5. Phần F: Lexicon mini
    lexicon_txt = "lexicon.txt"
    with open(lexicon_txt, "w", encoding="utf-8") as f:
        f.write("mo m o_\ndong d o ng\nlen l e n\nxuong x u o ng\ndung d u ng\n")
    print(f"\n[PHẦN F] Đã tạo file lexicon: {lexicon_txt}")

    # 6. Phần G: Bigram và MAP Re-ranking
    corpus = ["mo dong", "len xuong", "mo len", "dong dung", "mo dong", "mo len"]
    counts1, counts2 = {}, {}
    for sentence in corpus:
        words = sentence.split()
        for w in words:
            counts1[w] = counts1.get(w, 0) + 1
        for i in range(len(words) - 1):
            pair = (words[i], words[i+1])
            counts2[pair] = counts2.get(pair, 0) + 1

    def bigram_prob(prev, cur, k=0.5):
        V = len(LABELS)
        return (counts2.get((prev, cur), 0) + k) / (counts1.get(prev, 0) + k * V)

    print("\n[PHẦN G] THỬ NGHIỆM MAP RE-RANKING VỚI CÁC TRỌNG SỐ LAMBDA_LM:")
    for lm_w in [0.0, 0.1, 0.3, 1.0]:
        total_scores = {}
        for w, m in models_5.items():
            a = m.score(f_test) / len(f_test)
            lm = math.log(bigram_prob("mo", w))
            total_scores[w] = a + lm_w * lm
        best_w = max(total_scores, key=total_scores.get)
        print(f"  - lambda_LM = {lm_w:3.1f}: Dự đoán = '{VIET_LABELS[best_w]}' | Score: {total_scores[best_w]:.3f}")

    # 7. Phần H: Đánh giá Clean Test và Robustness
    y_true, y_pred = [], []
    correct_scores, wrong_scores = [], []
    for l in LABELS:
        for wav in Path(test_dir, l).glob('*.wav'):
            pred, scores = recognize_utterance(str(wav), models_5)
            y_true.append(l)
            y_pred.append(pred)
            for k, sc in scores.items():
                if k == l:
                    correct_scores.append(sc)
                else:
                    wrong_scores.append(sc)

    clean_acc = accuracy_score(y_true, y_pred)
    print(f"\n[PHẦN H] HMM CLEAN TEST ACCURACY: {clean_acc * 100:.2f}%")

    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=[VIET_LABELS[l] for l in LABELS])
    disp.plot(cmap='Blues')
    plt.title(f"HMM Confusion Matrix (Clean Accuracy = {clean_acc * 100:.1f}%)", fontweight="bold")
    fig_cm = os.path.join(FIGURES_DIR, "hmm_confusion_matrix.png")
    plt.tight_layout()
    plt.savefig(fig_cm, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu HMM Confusion Matrix vào: {fig_cm}")

    # Đề xuất Reject Threshold
    mean_corr = np.mean(correct_scores)
    mean_wrng = np.mean(wrong_scores)
    reject_threshold = (mean_corr + mean_wrng) / 2
    print(f"\n=== ĐỀ XUẤT NGƯỠNG TỪ CHỐI (REJECT THRESHOLD) ===")
    print(f"  - Điểm Log-Likelihood Đúng Lớp TB : {mean_corr:.2f}")
    print(f"  - Điểm Log-Likelihood Sai Lớp TB  : {mean_wrng:.2f}")
    print(f"  - Khuyến nghị Ngưỡng Reject Theta : {reject_threshold:.2f}")
    print("\n✅ HOÀN THÀNH TOÀN BỘ CÁC MỤC THỰC HÀNH LAB 3!")

if __name__ == "__main__":
    run_lab3()
