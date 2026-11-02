import os
import sys
import numpy as np
import scipy.signal as signal

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

TARGET_SR = 16000
FRAME_SHIFT_MS = 10
FRAME_LEN_MS = 25

# Phonetic / acoustic dictionary for Vietnamese HMM states
# Each token has 5 states with (f0_offset, f1, f2, f3, gain, is_voiced)
TOKEN_HMM_MODELS = {
    "mời": {
        "duration_frames": 45,
        "base_f0": 140, # huyền tone (falling)
        "tone_slope": -20,
        "formants": [550, 1100, 2400],
        "voiced": True
    },
    "khách": {
        "duration_frames": 38,
        "base_f0": 160, # sắc tone (rising)
        "tone_slope": +35,
        "formants": [720, 1350, 2500],
        "voiced": True
    },
    "hàng": {
        "duration_frames": 44,
        "base_f0": 135, # huyền tone (falling)
        "tone_slope": -18,
        "formants": [750, 1200, 2400],
        "voiced": True
    },
    "số": {
        "duration_frames": 40,
        "base_f0": 165, # sắc tone (rising)
        "tone_slope": +30,
        "formants": [480, 950, 2300],
        "voiced": True
    },
    "không": {
        "duration_frames": 42,
        "base_f0": 150, # ngang tone
        "tone_slope": 0,
        "formants": [450, 850, 2200],
        "voiced": True
    },
    "một": {
        "duration_frames": 35,
        "base_f0": 130, # nặng tone (drop low)
        "tone_slope": -25,
        "formants": [420, 900, 2300],
        "voiced": True
    },
    "hai": {
        "duration_frames": 42,
        "base_f0": 150, # ngang tone
        "tone_slope": +5,
        "formants": [700, 1750, 2600],
        "voiced": True
    },
    "ba": {
        "duration_frames": 42,
        "base_f0": 150, # ngang tone
        "tone_slope": -5,
        "formants": [720, 1220, 2450],
        "voiced": True
    },
    "bốn": {
        "duration_frames": 40,
        "base_f0": 165, # sắc tone (rising)
        "tone_slope": +30,
        "formants": [460, 920, 2300],
        "voiced": True
    },
    "năm": {
        "duration_frames": 44,
        "base_f0": 150, # ngang tone
        "tone_slope": 0,
        "formants": [680, 1300, 2400],
        "voiced": True
    },
    "sáu": {
        "duration_frames": 40,
        "base_f0": 165, # sắc tone
        "tone_slope": +35,
        "formants": [550, 1100, 2400],
        "voiced": True
    },
    "bảy": {
        "duration_frames": 42,
        "base_f0": 140, # hỏi tone (dip then rise)
        "tone_slope": -15,
        "formants": [620, 1450, 2500],
        "voiced": True
    },
    "tám": {
        "duration_frames": 38,
        "base_f0": 165, # sắc tone
        "tone_slope": +30,
        "formants": [700, 1250, 2400],
        "voiced": True
    },
    "chín": {
        "duration_frames": 38,
        "base_f0": 165, # sắc tone
        "tone_slope": +30,
        "formants": [380, 2100, 2800],
        "voiced": True
    },
    "đến": {
        "duration_frames": 38,
        "base_f0": 160, # sắc tone
        "tone_slope": +25,
        "formants": [450, 1850, 2600],
        "voiced": True
    },
    "quầy": {
        "duration_frames": 42,
        "base_f0": 135, # huyền tone
        "tone_slope": -20,
        "formants": [520, 1400, 2450],
        "voiced": True
    }
}

DIGIT = {
    "0": "không", "1": "một", "2": "hai", "3": "ba", "4": "bốn",
    "5": "năm", "6": "sáu", "7": "bảy", "8": "tám", "9": "chín"
}

def normalize_text_hmm(text):
    text = text.lower().replace(".", "").replace(",", "").replace("!", "").replace("?", "")
    out = []
    for tok in text.split():
        if tok.isdigit():
            out.extend(DIGIT[c] for c in tok if c in DIGIT)
        else:
            out.append(tok)
    return out

def synthesize_hmm(text, sr=TARGET_SR, duration_scale=1.0, f0_scale=1.0):
    """
    Parametric HMM-based Speech Synthesizer.
    Generates F0, duration, and formant trajectories from HMM state sequences,
    then resynthesizes speech using a Source-Filter Vocoder.
    """
    tokens = normalize_text_hmm(text)
    
    # 1. Generate frame-level acoustic trajectories from HMM states
    f0_frames = []
    f1_frames = []
    f2_frames = []
    f3_frames = []
    energy_frames = []
    state_alignment = []
    
    current_state_idx = 0
    silence_frames = 8
    
    # Initial silence
    f0_frames.extend([0.0] * silence_frames)
    f1_frames.extend([500.0] * silence_frames)
    f2_frames.extend([1500.0] * silence_frames)
    f3_frames.extend([2500.0] * silence_frames)
    energy_frames.extend([0.0] * silence_frames)
    state_alignment.extend([0] * silence_frames)
    
    for tok in tokens:
        model = TOKEN_HMM_MODELS.get(tok, {
            "duration_frames": 40,
            "base_f0": 150,
            "tone_slope": 0,
            "formants": [500, 1400, 2500],
            "voiced": True
        })
        
        n_frames = int(model["duration_frames"] * duration_scale)
        base_f0 = model["base_f0"] * f0_scale
        slope = model["tone_slope"] * f0_scale
        formants = model["formants"]
        
        # 5 states per phoneme/word in HMM
        frames_per_state = max(1, n_frames // 5)
        for s in range(5):
            s_frames = frames_per_state if s < 4 else (n_frames - frames_per_state * 4)
            current_state_idx += 1
            progress_start = s / 5.0
            progress_end = (s + 1) / 5.0
            
            for f in range(s_frames):
                p = progress_start + (progress_end - progress_start) * (f / max(1, s_frames))
                # F0 contour with tone slope
                cur_f0 = base_f0 + slope * (p - 0.5)
                # Formant trajectory with state interpolation
                cur_f1 = formants[0] * (0.95 + 0.1 * np.sin(np.pi * p))
                cur_f2 = formants[1] * (0.96 + 0.08 * np.cos(np.pi * p))
                cur_f3 = formants[2]
                # Raised-cosine energy window for state/unit
                cur_en = np.sin(np.pi * p) ** 0.5 * 0.12
                
                f0_frames.append(cur_f0)
                f1_frames.append(cur_f1)
                f2_frames.append(cur_f2)
                f3_frames.append(cur_f3)
                energy_frames.append(cur_en)
                state_alignment.append(current_state_idx)
                
        # Inter-word short pause
        pause_frames = 4
        f0_frames.extend([0.0] * pause_frames)
        f1_frames.extend([f1_frames[-1]] * pause_frames)
        f2_frames.extend([f2_frames[-1]] * pause_frames)
        f3_frames.extend([f3_frames[-1]] * pause_frames)
        energy_frames.extend([0.0] * pause_frames)
        state_alignment.extend([current_state_idx] * pause_frames)

    # Final silence
    f0_frames.extend([0.0] * silence_frames)
    f1_frames.extend([500.0] * silence_frames)
    f2_frames.extend([1500.0] * silence_frames)
    f3_frames.extend([2500.0] * silence_frames)
    energy_frames.extend([0.0] * silence_frames)
    state_alignment.extend([0] * silence_frames)

    # 2. Dynamic feature smoothing (MLPG simulation using moving average / filter)
    f0_array = np.array(f0_frames, dtype=np.float32)
    # Smooth only non-zero voiced segments
    voiced_mask = f0_array > 0
    if np.any(voiced_mask):
        smoothed_f0 = np.copy(f0_array)
        kernel = np.ones(5) / 5.0
        # convolution on voiced regions
        f0_voiced = signal.medfilt(f0_array, kernel_size=5)
        smoothed_f0[voiced_mask] = f0_voiced[voiced_mask]
        f0_array = smoothed_f0

    f1_array = signal.medfilt(np.array(f1_frames, dtype=np.float32), 5)
    f2_array = signal.medfilt(np.array(f2_frames, dtype=np.float32), 5)
    f3_array = signal.medfilt(np.array(f3_frames, dtype=np.float32), 5)
    en_array = np.array(energy_frames, dtype=np.float32)
    
    # 3. Parametric Source-Filter Waveform Generation
    hop_samples = int(sr * FRAME_SHIFT_MS / 1000)
    total_samples = len(f0_array) * hop_samples
    waveform = np.zeros(total_samples, dtype=np.float32)
    
    # Excitation generation
    phase = 0.0
    for idx, (f0, en) in enumerate(zip(f0_array, en_array)):
        start_samp = idx * hop_samples
        end_samp = start_samp + hop_samples
        if end_samp > total_samples:
            break
            
        n_pts = end_samp - start_samp
        if f0 > 30 and en > 0.001:
            # Voiced excitation: quasi-periodic glottal pulse train
            period_samples = sr / f0
            samples_in_frame = np.arange(n_pts)
            inst_phase = (phase + samples_in_frame / period_samples) % 1.0
            # Rosenberg glottal pulse approximation: N1 samples rise, N2 samples fall
            glottal_pulse = np.sin(np.pi * inst_phase) * (inst_phase < 0.6)
            # Add slight harmonics for natural vocal buzz
            harmonics = 0.3 * np.sin(2 * np.pi * inst_phase) + 0.15 * np.sin(4 * np.pi * inst_phase)
            exc = (glottal_pulse + harmonics) * en
            phase = (phase + n_pts / period_samples) % 1.0
        else:
            # Unvoiced / Silence: Gaussian noise shaped by low energy
            exc = np.random.normal(0, 0.03, n_pts) * (en if en > 0 else 0.0)
            phase = 0.0
            
        waveform[start_samp:end_samp] = exc

    # 4. Vocal tract filtering (Cascade of 3 formant resonators)
    def make_resonator(fc, bw, fs):
        # 2nd-order all-pole IIR filter
        r = np.exp(-np.pi * bw / fs)
        theta = 2 * np.pi * fc / fs
        a1 = -2 * r * np.cos(theta)
        a2 = r * r
        b0 = 1 - r
        return [b0], [1.0, a1, a2]

    mean_f1 = float(np.mean(f1_array))
    mean_f2 = float(np.mean(f2_array))
    mean_f3 = float(np.mean(f3_array))
    
    b1, a1 = make_resonator(mean_f1, 90, sr)
    b2, a2 = make_resonator(mean_f2, 110, sr)
    b3, a3 = make_resonator(mean_f3, 140, sr)
    
    filtered = signal.lfilter(b1, a1, waveform)
    filtered = signal.lfilter(b2, a2, filtered)
    filtered = signal.lfilter(b3, a3, filtered)
    
    # Radiation effect (lip radiation zero at z=0.97)
    radiation_b = [1.0, -0.97]
    y_hmm = signal.lfilter(radiation_b, [1.0], filtered)
    
    # Normalize
    max_val = np.max(np.abs(y_hmm))
    if max_val > 0:
        y_hmm = 0.85 * (y_hmm / max_val)
        
    frame_times = np.arange(len(f0_array)) * (FRAME_SHIFT_MS / 1000.0)
    
    tracks = {
        "f0": f0_array,
        "f1": f1_array,
        "f2": f2_array,
        "f3": f3_array,
        "energy": en_array,
        "states": np.array(state_alignment),
        "frame_times": frame_times,
        "text": text
    }
    
    return y_hmm.astype(np.float32), sr, tracks

if __name__ == "__main__":
    sentence = "Mời khách hàng số 23 đến quầy 5"
    print(f"Synthesizing HMM speech for: '{sentence}'...")
    audio, sr, tr = synthesize_hmm(sentence)
    print(f"Success! Audio length: {len(audio)/sr:.2f}s, Tracks F0 points: {len(tr['f0'])}")
    import soundfile as sf
    sf.write("audio_output/hmm_tts.wav", audio, sr)
    print("Saved test audio to audio_output/hmm_tts.wav")

