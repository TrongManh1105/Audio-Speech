import os
import io
import time
import sys
import numpy as np
import soundfile as sf
import librosa
from gtts import gTTS

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TARGET_SR = 16000

CACHE_DIR = os.path.join(os.path.dirname(__file__), "neural_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def synthesize(text, voice="vi_female", sr=TARGET_SR):
    """
    Neural TTS Synthesizer wrapper using pretrained neural TTS.
    Outputs waveform, sample rate, and extra dictionary with latency and mel-spectrogram.
    """
    t0 = time.time()
    sanitized_name = "".join(c for c in text.lower() if c.isalnum())[:30] + ".wav"
    cache_path = os.path.join(CACHE_DIR, sanitized_name)
    
    if os.path.exists(cache_path):
        y, orig_sr = sf.read(cache_path, dtype="float32")
        if orig_sr != sr:
            y = librosa.resample(y, orig_sr=orig_sr, target_sr=sr)
    else:
        # Generate via neural synthesis
        tts = gTTS(text=text, lang="vi", slow=False)
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)
        
        y, orig_sr = sf.read(mp3_fp, dtype="float32")
        if y.ndim > 1:
            y = y.mean(axis=1)
        if orig_sr != sr:
            y = librosa.resample(y, orig_sr=orig_sr, target_sr=sr)
            
        # Light trim
        y, _ = librosa.effects.trim(y, top_db=30)
        # Normalize
        max_val = np.max(np.abs(y))
        if max_val > 0:
            y = 0.9 * (y / max_val)
            
        sf.write(cache_path, y, sr, subtype="PCM_16")

    latency = time.time() - t0
    
    # Extract mel-spectrogram
    mel = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=80)
    mel_db = librosa.power_to_db(mel, ref=np.max)
    
    extra = {
        "latency": round(latency, 4),
        "mel_spectrogram": mel_db,
        "sample_rate": sr,
        "text": text
    }
    
    return y.astype(np.float32), sr, extra

if __name__ == "__main__":
    test_sentence = "Mời khách hàng số 23 đến quầy 5"
    print(f"Synthesizing Neural TTS for: '{test_sentence}'...")
    audio, sr, info = synthesize(test_sentence)
    print(f"Success! Latency: {info['latency']}s, Duration: {len(audio)/sr:.2f}s, Mel shape: {info['mel_spectrogram'].shape}")
    os.makedirs("audio_output", exist_ok=True)
    sf.write("audio_output/neural_tts.wav", audio, sr)
    print("Saved neural audio to audio_output/neural_tts.wav")
