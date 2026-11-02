import os
import sys
import numpy as np
import soundfile as sf
import librosa
from gtts import gTTS
import io

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

TARGET_SR = 16000

def generate_word_variations(word_text, count, base_speed_range=(0.85, 1.15), base_pitch_range=(-2, 2)):
    """
    Sinh các biến thể tự nhiên của từ nói bằng gTTS + time-stretch + pitch-shift
    để tạo dữ liệu nói đa dạng cho huấn luyện và kiểm thử.
    """
    tts = gTTS(text=word_text, lang='vi', slow=False)
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    
    y, sr = sf.read(fp, dtype="float32")
    if y.ndim > 1:
        y = y.mean(axis=1)
    if sr != TARGET_SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=TARGET_SR)
    
    y, _ = librosa.effects.trim(y, top_db=25)
    
    variations = []
    np.random.seed(42 + hash(word_text) % 1000)
    
    for i in range(count):
        rate = np.random.uniform(base_speed_range[0], base_speed_range[1])
        pitch_step = np.random.uniform(base_pitch_range[0], base_pitch_range[1])
        
        # Biến đổi tốc độ và cao độ nhẹ nhàng để tạo các lần nói khác nhau
        y_mod = librosa.effects.time_stretch(y, rate=rate)
        if abs(pitch_step) > 0.3:
            y_mod = librosa.effects.pitch_shift(y_mod, sr=TARGET_SR, n_steps=pitch_step)
            
        # Thêm khoảng lặng đầu và đuôi (0.2s - 0.4s) như yêu cầu của Lab 2 & 3
        sil_front = np.zeros(int(TARGET_SR * np.random.uniform(0.2, 0.35)), dtype=np.float32)
        sil_back = np.zeros(int(TARGET_SR * np.random.uniform(0.2, 0.35)), dtype=np.float32)
        
        # Thêm một chút nhiễu phòng rất nhỏ (SNR cao ~40dB)
        noise = np.random.normal(0, 0.002, len(y_mod))
        y_mod = y_mod + noise
        
        full_audio = np.concatenate([sil_front, y_mod, sil_back])
        # Chuẩn hóa biên độ
        max_val = np.max(np.abs(full_audio))
        if max_val > 0:
            full_audio = 0.9 * (full_audio / max_val)
            
        variations.append(full_audio.astype(np.float32))
        
    return variations

def main():
    print("Bắt đầu khởi tạo dữ liệu chuẩn cho Lab 2 và Lab 3...")
    
    # -------------------------------------------------------------
    # 1. TẠO DỮ LIỆU LAB 2: dataset/ (5 từ x 5 lần lặp = 25 file)
    # -------------------------------------------------------------
    lab2_words = {
        "khong": "không",
        "mot": "một",
        "hai": "hai",
        "ba": "ba",
        "bon": "bốn"
    }
    
    for folder, viet_word in lab2_words.items():
        dir_path = os.path.join("dataset", folder)
        os.makedirs(dir_path, exist_ok=True)
        var_audios = generate_word_variations(viet_word, count=5)
        for idx, audio in enumerate(var_audios, 1):
            out_file = os.path.join(dir_path, f"{folder}_{idx:02d}.wav")
            sf.write(out_file, audio, TARGET_SR, subtype="PCM_16")
    print("✅ Đã tạo xong dataset Lab 2 (25 file trong dataset/)")
    
    # -------------------------------------------------------------
    # 2. TẠO DỮ LIỆU LAB 3: dataset_lab3/ (5 lệnh x 8 file: 6 train + 2 test)
    # -------------------------------------------------------------
    lab3_words = {
        "mo": "mở",
        "dong": "đóng",
        "len": "lên",
        "xuong": "xuống",
        "dung": "dừng"
    }
    
    for folder, viet_word in lab3_words.items():
        train_dir = os.path.join("dataset_lab3", "train", folder)
        test_dir = os.path.join("dataset_lab3", "test", folder)
        os.makedirs(train_dir, exist_ok=True)
        os.makedirs(test_dir, exist_ok=True)
        
        var_audios = generate_word_variations(viet_word, count=8)
        # 6 file train
        for idx in range(1, 7):
            out_file = os.path.join(train_dir, f"{folder}_{idx:02d}.wav")
            sf.write(out_file, var_audios[idx-1], TARGET_SR, subtype="PCM_16")
        # 2 file test
        for idx in range(7, 9):
            out_file = os.path.join(test_dir, f"{folder}_{idx:02d}.wav")
            sf.write(out_file, var_audios[idx-1], TARGET_SR, subtype="PCM_16")
            
    print("✅ Đã tạo xong dataset Lab 3 (40 file trong dataset_lab3/train và test)")
    
    # -------------------------------------------------------------
    # 3. TẠO FILE AUDIO MẪU CHO LAB 1: audio/input.wav
    # -------------------------------------------------------------
    os.makedirs("audio", exist_ok=True)
    input_wav = "audio/input.wav"
    if not os.path.exists(input_wav):
        # Trích xuất từ IMG_5237.MOV nếu có, hoặc tạo file audio mẫu chuẩn
        if os.path.exists("IMG_5237.MOV"):
            try:
                y_mov, sr_mov = librosa.load("IMG_5237.MOV", sr=44100, mono=False, duration=30)
                if y_mov.ndim == 1:
                    y_mov = np.vstack([y_mov, y_mov])
                sf.write(input_wav, y_mov.T, sr_mov, subtype="PCM_16")
                print("✅ Đã trích xuất audio mẫu stereo 44.1kHz từ IMG_5237.MOV vào audio/input.wav")
            except Exception as e:
                print(f"Không thể đọc trực tiếp MOV ({e}), đang tạo audio thử nghiệm...")
        if not os.path.exists(input_wav):
            # Tạo audio stereo 44.1kHz chất lượng cao
            duration = 15.0
            sr = 44100
            t = np.linspace(0, duration, int(sr * duration), endpoint=False)
            ch1 = 0.5 * np.sin(2 * np.pi * 220 * t) + 0.3 * np.sin(2 * np.pi * 440 * t) + 0.2 * np.sin(2 * np.pi * 880 * t)
            ch2 = 0.5 * np.sin(2 * np.pi * 261.6 * t) + 0.3 * np.sin(2 * np.pi * 523.2 * t) + 0.2 * np.sin(2 * np.pi * 1046.5 * t)
            stereo = np.vstack([ch1, ch2]).T
            sf.write(input_wav, stereo, sr, subtype="PCM_16")
            print("✅ Đã tạo file audio stereo 44.1kHz mẫu tại audio/input.wav")

if __name__ == "__main__":
    main()

