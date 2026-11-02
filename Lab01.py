import os
import sys
import numpy as np
import soundfile as sf
import librosa
import librosa.display
import matplotlib.pyplot as plt
from scipy import signal

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

AUDIO_DIR = "audio"
FIGURES_DIR = "figures_lab1"
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def run_lab1():
    print("=" * 70)
    print("CSE457 - BÀI THỰC HÀNH LAB 1: PHÂN TÍCH VÀ XỬ LÝ TÍN HIỆU ÂM THANH SỐ")
    print("Sinh viên: Nguyễn Trọng Mạnh Tiến - MSV: 2351260689 - Lớp: 65TTNT")
    print("=" * 70)

    # -------------------------------------------------------------
    # PHẦN A: ĐỌC VÀ KIỂM TRA DỮ LIỆU ÂM THANH
    # -------------------------------------------------------------
    input_path = os.path.join(AUDIO_DIR, "input.wav")
    if not os.path.exists(input_path):
        # Tạo tín hiệu đa kênh mẫu chất lượng cao 44.1kHz stereo nếu chưa có
        sr = 44100
        duration = 10.0
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        ch1 = 0.6 * np.sin(2 * np.pi * 220 * t) + 0.3 * np.sin(2 * np.pi * 440 * t) + 0.1 * np.sin(2 * np.pi * 880 * t)
        ch2 = 0.5 * np.sin(2 * np.pi * 330 * t) + 0.3 * np.sin(2 * np.pi * 660 * t) + 0.2 * np.sin(2 * np.pi * 1320 * t)
        stereo_sig = np.vstack([ch1, ch2]).T
        sf.write(input_path, stereo_sig, sr, subtype="PCM_16")

    # Đọc thông tin tệp
    info = sf.info(input_path)
    Fs = info.samplerate
    channels = info.channels
    duration = info.duration
    file_size_bytes = os.path.getsize(input_path)

    print(f"\n[PHẦN A] THÔNG SỐ TỆP ÂM THANH GỐC ({input_path}):")
    print(f"  - Sampling Rate (Fs) : {Fs} Hz (Nyquist: {Fs/2} Hz)")
    print(f"  - Số kênh (Channels) : {channels} ({'Stereo' if channels == 2 else 'Mono'})")
    print(f"  - Thời lượng        : {duration:.3f} s")
    print(f"  - Subtype / Bitdepth: {info.subtype}")
    print(f"  - Dung lượng tệp     : {file_size_bytes:,} bytes (~{file_size_bytes / (1024*1024):.2f} MB)")

    # Đọc dữ liệu float32
    data, sr = sf.read(input_path, dtype="float32")
    if channels > 1:
        mono_x = data.mean(axis=1)
        rms_ch1 = np.sqrt(np.mean(data[:, 0]**2))
        rms_ch2 = np.sqrt(np.mean(data[:, 1]**2))
        print(f"  - RMS Kênh Trái: {rms_ch1:.4f} | RMS Kênh Phải: {rms_ch2:.4f}")
    else:
        mono_x = data

    # Chuẩn hóa về [-1.0, 1.0]
    peak_val = np.max(np.abs(mono_x))
    if peak_val > 0:
        mono_x = mono_x / peak_val

    # -------------------------------------------------------------
    # PHẦN B: PHÂN TÍCH MIỀN THỜI GIAN
    # -------------------------------------------------------------
    peak = np.max(np.abs(mono_x))
    rms_val = np.sqrt(np.mean(mono_x**2))
    energy_val = np.sum(mono_x**2)
    is_clipping = np.sum(np.abs(mono_x) >= 0.999) > 0

    print(f"\n[PHẦN B] ĐẶC TRƯNG MIỀN THỜI GIAN:")
    print(f"  - Peak: {peak:.4f} | RMS: {rms_val:.4f} (-{20*np.log10(1/rms_val):.2f} dBFS) | Năng lượng E: {energy_val:.2f}")
    print(f"  - Nguy cơ Clipping: {'CÓ (Cảnh báo biến dạng)' if is_clipping else 'KHÔNG (An toàn)'}")

    # Vẽ Waveform toàn tệp và zoom 1 giây
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6))
    time_axis = np.arange(len(mono_x)) / Fs
    ax1.plot(time_axis, mono_x, color="#1f77b4", linewidth=0.7)
    ax1.set_title("Waveform toàn bộ tệp âm thanh", fontweight="bold")
    ax1.set_ylabel("Biên độ")
    ax1.grid(True, linestyle=":", alpha=0.6)

    # Zoom đoạn 1.0s đến 2.0s
    start_s, end_s = 1.0, min(2.0, duration)
    s_idx, e_idx = int(start_s * Fs), int(end_s * Fs)
    ax2.plot(time_axis[s_idx:e_idx], mono_x[s_idx:e_idx], color="#ff7f0e", linewidth=1.0)
    ax2.set_title(f"Waveform phóng to đoạn {start_s}s - {end_s}s (Chi tiết dao động chu kỳ)", fontweight="bold")
    ax2.set_xlabel("Thời gian (giây)")
    ax2.set_ylabel("Biên độ")
    ax2.grid(True, linestyle=":", alpha=0.6)

    fig_waveform = os.path.join(FIGURES_DIR, "waveform.png")
    plt.tight_layout()
    plt.savefig(fig_waveform, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu biểu đồ waveform vào: {fig_waveform}")

    # -------------------------------------------------------------
    # PHẦN C: PHÂN TÍCH MIỀN TẦN SỐ BẰNG FFT
    # -------------------------------------------------------------
    seg = mono_x[s_idx:e_idx]
    w = np.hamming(len(seg))
    seg_w = seg * w

    # So sánh 2 mức NFFT: 2048 và 8192
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 6), sharex=True)
    peaks_detected = []

    for idx, (nfft, ax, col) in enumerate([(2048, ax1, "#1f77b4"), (8192, ax2, "#2ca02c")]):
        X = np.fft.rfft(seg_w, n=nfft)
        freqs = np.fft.rfftfreq(nfft, 1 / Fs)
        mag_db = 20 * np.log10(np.maximum(np.abs(X), 1e-10))
        delta_f = Fs / nfft
        ax.plot(freqs, mag_db, color=col, linewidth=0.9, label=f"NFFT={nfft} (Δf={delta_f:.2f} Hz)")
        ax.set_title(f"Phổ FFT với NFFT={nfft} (Khoảng cách bin Δf = {delta_f:.2f} Hz)", fontweight="bold")
        ax.set_ylabel("Biên độ (dB)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.set_xlim(0, 5000)
        ax.legend(loc="upper right")

        if idx == 1: # Tìm đỉnh trên NFFT=8192
            pk_indices, _ = signal.find_peaks(mag_db, height=-40, distance=int(100/delta_f))
            top_pks = sorted(pk_indices, key=lambda i: mag_db[i], reverse=True)[:4]
            for p in top_pks:
                peaks_detected.append(freqs[p])
                ax.plot(freqs[p], mag_db[p], "rx")
                ax.annotate(f"{freqs[p]:.1f} Hz", (freqs[p], mag_db[p] + 3), fontsize=9, color="red")

    ax2.set_xlabel("Tần số (Hz)")
    fig_fft = os.path.join(FIGURES_DIR, "fft.png")
    plt.tight_layout()
    plt.savefig(fig_fft, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu biểu đồ phổ FFT vào: {fig_fft}")
    print(f"  - Các đỉnh phổ tiêu biểu tìm thấy: {[f'{p:.1f} Hz' for p in sorted(peaks_detected)]}")

    # -------------------------------------------------------------
    # PHẦN D: STFT VÀ SPECTROGRAM (SO SÁNH 3 FRAME LENGTHS)
    # -------------------------------------------------------------
    frame_lengths_ms = [10, 25, 50]
    fig, axes = plt.subplots(3, 1, figsize=(13, 8), sharex=True)

    for i, f_ms in enumerate(frame_lengths_ms):
        n_per_seg = int(Fs * f_ms / 1000)
        n_overlap = int(n_per_seg * 0.6)
        nfft_val = max(2048, int(2**np.ceil(np.log2(n_per_seg))))
        f_stft, t_stft, Zxx = signal.spectrogram(
            mono_x[:int(Fs * min(10.0, duration))], fs=Fs, window='hamming',
            nperseg=n_per_seg, noverlap=n_overlap, nfft=nfft_val, mode='magnitude'
        )
        S_db = 20 * np.log10(np.maximum(Zxx, 1e-10))
        img = axes[i].pcolormesh(t_stft, f_stft, S_db, shading='gouraud', cmap='magma', vmin=-100, vmax=0)
        axes[i].set_title(f"Spectrogram Frame Length = {f_ms} ms (Độ dài khung N={n_per_seg} mẫu)", fontweight="bold")
        axes[i].set_ylabel("Tần số (Hz)")
        axes[i].set_ylim(0, 6000)

    axes[-1].set_xlabel("Thời gian (giây)")
    fig_spec = os.path.join(FIGURES_DIR, "spectrogram.png")
    plt.tight_layout()
    plt.savefig(fig_spec, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu so sánh spectrogram (10ms, 25ms, 50ms) vào: {fig_spec}")

    # -------------------------------------------------------------
    # PHẦN E: THÍ NGHIỆM CỬA SỔ (WINDOWING EXPERIMENT)
    # -------------------------------------------------------------
    frame_test = mono_x[s_idx : s_idx + 1024]
    w_rect = np.ones(len(frame_test))
    w_hamm = np.hamming(len(frame_test))

    fft_rect = np.fft.rfft(frame_test * w_rect, n=8192)
    fft_hamm = np.fft.rfft(frame_test * w_hamm, n=8192)
    f_w = np.fft.rfftfreq(8192, 1 / Fs)

    plt.figure(figsize=(12, 4.5))
    plt.plot(f_w, 20 * np.log10(np.maximum(np.abs(fft_rect), 1e-10)), label="Cửa sổ Chữ nhật (Rectangular - Main-lobe hẹp, Rò rỉ lớn)", color="red", alpha=0.7)
    plt.plot(f_w, 20 * np.log10(np.maximum(np.abs(fft_hamm), 1e-10)), label="Cửa sổ Hamming (Main-lobe rộng hơn, Suy hao side-lobe cao)", color="blue", linewidth=1.5)
    plt.xlim(0, 4000)
    plt.title("So sánh Rò rỉ Phổ (Spectral Leakage) giữa Rectangular và Hamming", fontweight="bold")
    plt.xlabel("Tần số (Hz)")
    plt.ylabel("Biên độ (dB)")
    plt.legend()
    plt.grid(True, linestyle=":", alpha=0.6)
    
    fig_win = os.path.join(FIGURES_DIR, "window_comparison.png")
    plt.tight_layout()
    plt.savefig(fig_win, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu so sánh cửa sổ vào: {fig_win}")

    # -------------------------------------------------------------
    # PHẦN F: LỌC SỐ FIR (LOW-PASS 2kHz VÀ HIGH-PASS 1kHz)
    # -------------------------------------------------------------
    numtaps = 201
    group_delay_samples = (numtaps - 1) / 2
    group_delay_ms = (group_delay_samples / Fs) * 1000

    # Thiết kế FIR Low-pass 2 kHz
    b_lpf = signal.firwin(numtaps=numtaps, cutoff=2000.0, fs=Fs, window='hamming')
    y_lpf = signal.lfilter(b_lpf, [1.0], mono_x)
    sf.write(os.path.join(AUDIO_DIR, "filtered_lowpass_2k.wav"), y_lpf, Fs)

    # Thiết kế FIR High-pass 1 kHz
    b_hpf = signal.firwin(numtaps=numtaps, cutoff=1000.0, fs=Fs, pass_zero=False, window='hamming')
    y_hpf = signal.lfilter(b_hpf, [1.0], mono_x)
    sf.write(os.path.join(AUDIO_DIR, "filtered_highpass_1k.wav"), y_hpf, Fs)

    # Vẽ đáp ứng tần số
    w_resp, h_lpf = signal.freqz(b_lpf, worN=4096, fs=Fs)
    _, h_hpf = signal.freqz(b_hpf, worN=4096, fs=Fs)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6))
    ax1.plot(w_resp, 20 * np.log10(np.maximum(np.abs(h_lpf), 1e-6)), color="blue", label="FIR Low-Pass (fc = 2 kHz)")
    ax1.plot(w_resp, 20 * np.log10(np.maximum(np.abs(h_hpf), 1e-6)), color="green", label="FIR High-Pass (fc = 1 kHz)")
    ax1.set_title(f"Đáp ứng tần số bộ lọc FIR đối xứng 201 taps (Group Delay = {group_delay_ms:.2f} ms)", fontweight="bold")
    ax1.set_ylabel("Biên độ (dB)")
    ax1.set_ylim(-100, 5)
    ax1.grid(True, linestyle=":", alpha=0.6)
    ax1.legend()

    # So sánh phổ trước và sau Low-pass
    fft_orig = np.abs(np.fft.rfft(mono_x[s_idx:e_idx] * np.hamming(e_idx - s_idx), n=4096))
    fft_filt = np.abs(np.fft.rfft(y_lpf[s_idx:e_idx] * np.hamming(e_idx - s_idx), n=4096))
    f_cmpr = np.fft.rfftfreq(4096, 1 / Fs)

    ax2.plot(f_cmpr, 20*np.log10(np.maximum(fft_orig, 1e-6)), label="Phổ gốc trước lọc", alpha=0.6, color="gray")
    ax2.plot(f_cmpr, 20*np.log10(np.maximum(fft_filt, 1e-6)), label="Phổ sau khi qua Low-pass 2 kHz", color="blue")
    ax2.set_title("So sánh Phổ trước và sau khi lọc Low-pass 2 kHz", fontweight="bold")
    ax2.set_xlabel("Tần số (Hz)")
    ax2.set_ylabel("Biên độ (dB)")
    ax2.grid(True, linestyle=":", alpha=0.6)
    ax2.legend()

    fig_filt = os.path.join(FIGURES_DIR, "filter_response.png")
    plt.tight_layout()
    plt.savefig(fig_filt, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu đáp ứng bộ lọc FIR vào: {fig_filt}")

    # -------------------------------------------------------------
    # PHẦN G: LƯỢNG TỬ HÓA, RESAMPLING VÀ MÃ HÓA
    # -------------------------------------------------------------
    def quantize(x_in, B):
        qmax = 2**(B - 1) - 1
        return np.round(np.clip(x_in, -1.0, 1.0) * qmax) / qmax

    def calc_snr(orig, x_q):
        e = x_q - orig
        return 10 * np.log10(np.sum(orig**2) / np.maximum(np.sum(e**2), 1e-12))

    bits = [4, 6, 8, 12, 16]
    snr_measured = []
    snr_theory = []

    for b in bits:
        xq = quantize(mono_x, b)
        measured = calc_snr(mono_x, xq)
        theory = 6.02 * b + 4.77 - 20 * np.log10(1.0 / rms_val)
        snr_measured.append(measured)
        snr_theory.append(theory)
        if b in [4, 8]:
            sf.write(os.path.join(AUDIO_DIR, f"quantized_{b}bit.wav"), xq, Fs)

    print("\n[PHẦN G] KẾT QUẢ ĐO SNR LƯỢNG TỬ:")
    for b, m, th in zip(bits, snr_measured, snr_theory):
        print(f"  - B = {b:2d} bit: SNR Đo được = {m:5.2f} dB | SNR Lý thuyết = {th:5.2f} dB")

    # Resampling về 16kHz và 8kHz
    x_16k = librosa.resample(mono_x, orig_sr=Fs, target_sr=16000)
    x_8k = librosa.resample(mono_x, orig_sr=Fs, target_sr=8000)
    sf.write(os.path.join(AUDIO_DIR, "resampled_16k.wav"), x_16k, 16000)
    sf.write(os.path.join(AUDIO_DIR, "resampled_8k.wav"), x_8k, 8000)

    # Tính toán Bitrate và Mức nén
    R_pcm_stereo = Fs * 16 * 2 # 1,411,200 bps
    size_pcm_mb = (R_pcm_stereo * duration / 8) / (1024 * 1024)
    size_mp3_256 = (256000 * duration / 8) / (1024 * 1024)
    size_mp3_128 = (128000 * duration / 8) / (1024 * 1024)

    cr_256 = R_pcm_stereo / 256000
    cr_128 = R_pcm_stereo / 128000

    print(f"\n[PHẦN G] TỐC ĐỘ BIT VÀ TỶ LỆ NÉN (Thời lượng: {duration:.2f}s):")
    print(f"  - PCM 16-bit Stereo : {R_pcm_stereo:,} bps | Dung lượng: {size_pcm_mb:.2f} MB")
    print(f"  - MP3 256 kbps      : 256,000 bps | Dung lượng: {size_mp3_256:.2f} MB | Tỷ lệ nén: {cr_256:.2f}:1 (Tiết kiệm {(1 - 1/cr_256)*100:.1f}%)")
    print(f"  - MP3 128 kbps      : 128,000 bps | Dung lượng: {size_mp3_128:.2f} MB | Tỷ lệ nén: {cr_128:.2f}:1 (Tiết kiệm {(1 - 1/cr_128)*100:.1f}%)")

    # Vẽ đồ thị SNR
    plt.figure(figsize=(8, 4.5))
    plt.plot(bits, snr_measured, "o-", color="blue", linewidth=1.5, label="SNR đo được thực tế")
    plt.plot(bits, snr_theory, "--", color="red", linewidth=1.5, label="SNR lý thuyết (6B + 4.77 - 20log10(1/RMS))")
    plt.title("Đánh giá SNR theo số bit lượng tử (Quy luật 6 dB/bit)", fontweight="bold")
    plt.xlabel("Số bit (B)")
    plt.ylabel("SNR (dB)")
    plt.grid(True, linestyle=":", alpha=0.6)
    plt.legend()
    fig_snr = os.path.join(FIGURES_DIR, "quantization_snr.png")
    plt.tight_layout()
    plt.savefig(fig_snr, dpi=180)
    plt.close()
    print(f"  [+] Đã lưu biểu đồ SNR vào: {fig_snr}")

    print("\n✅ HOÀN THÀNH TOÀN BỘ CÁC MỤC THỰC HÀNH LAB 1!")

if __name__ == "__main__":
    run_lab1()
