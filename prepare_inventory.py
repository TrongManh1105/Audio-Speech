import asyncio
import os
import io
import csv
import sys
import numpy as np
import soundfile as sf
import librosa
import edge_tts

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


WORDS = {
    "moi": "mời",
    "khach": "khách",
    "hang": "hàng",
    "so": "số",
    "khong": "không",
    "mot": "một",
    "hai": "hai",
    "ba": "ba",
    "bon": "bốn",
    "nam": "năm",
    "sau": "sáu",
    "bay": "bảy",
    "tam": "tám",
    "chin": "chín",
    "den": "đến",
    "quay": "quầy"
}

VOICES = {
    "01": ("vi-VN-HoaiMyNeural", "Speaker_Female"),
    "02": ("vi-VN-NamMinhNeural", "Speaker_Male")
}

TARGET_SR = 16000

def compute_rms(x):
    return float(np.sqrt(np.mean(x**2) + 1e-12))

async def synthesize_word(text, voice_name):
    communicate = edge_tts.Communicate(text, voice_name)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def process_audio(raw_bytes, target_sr=TARGET_SR):
    # Read audio from bytes using soundfile or librosa
    bio = io.BytesIO(raw_bytes)
    x, sr = sf.read(bio, dtype="float32")
    if x.ndim > 1:
        x = x.mean(axis=1)
    
    # Resample to 16kHz if needed
    if sr != target_sr:
        x = librosa.resample(x, orig_sr=sr, target_sr=target_sr)
    
    # Trim silence (top_db=28)
    trimmed, index = librosa.effects.trim(x, top_db=28)
    
    # Pad 100ms context silence at beginning and end as required in section 5.1
    silence_samples = int(target_sr * 0.1) # 100 ms
    pad_front = np.zeros(silence_samples, dtype=np.float32)
    pad_back = np.zeros(silence_samples, dtype=np.float32)
    x_out = np.concatenate([pad_front, trimmed, pad_back])
    
    # Light normalization to keep RMS reasonable (approx 0.08)
    cur_rms = compute_rms(x_out)
    if cur_rms > 0:
        # Avoid clipping
        x_out = x_out * (0.08 / cur_rms)
        x_out = np.clip(x_out, -0.95, 0.95)
    
    return x_out, target_sr

async def main():
    os.makedirs("lab4_data/units", exist_ok=True)
    metadata_rows = []
    
    print(f"Bắt đầu tạo {len(WORDS) * 2} file unit âm thanh...")
    
    for key, word_text in WORDS.items():
        for cand_id, (voice_name, spk_label) in VOICES.items():
            filename = f"{key}_{cand_id}.wav"
            filepath = os.path.join("lab4_data", "units", filename)
            
            # Synthesize
            raw_mp3 = await synthesize_word(word_text, voice_name)
            
            # Process & clean
            audio_pcm, sr = process_audio(raw_mp3, target_sr=TARGET_SR)
            
            # Save 16-bit PCM WAV
            sf.write(filepath, audio_pcm, sr, subtype="PCM_16")
            
            duration = len(audio_pcm) / sr
            unit_rms = compute_rms(audio_pcm)
            
            metadata_rows.append({
                "unit_id": f"{key}_{cand_id}",
                "label": word_text,
                "speaker": spk_label,
                "duration": round(duration, 4),
                "rms": round(unit_rms, 4),
                "file_path": filepath.replace("\\", "/")
            })
            print(f"  [+] Đã tạo {filename} (Độ dài: {duration:.3f}s, RMS: {unit_rms:.4f})")
            
    # Save metadata.csv
    csv_path = os.path.join("lab4_data", "metadata.csv")
    with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["unit_id", "label", "speaker", "duration", "rms", "file_path"])
        writer.writeheader()
        writer.writerows(metadata_rows)
        
    print(f"\n[OK] Đã hoàn thành tạo Inventory và lưu metadata vào {csv_path}!")

if __name__ == "__main__":
    asyncio.run(main())
