import numpy as np
from vosk import Model, KaldiRecognizer
from scipy.signal import resample
import json

model = Model("vosk-model")

def distort(audio, snr_db=10):
    rms = np.sqrt(np.mean(audio ** 2))
    noise_std = rms / (10 ** (snr_db / 20))
    noise = np.random.normal(0, noise_std, audio.shape)
    return audio + noise

def normalize(audio):
    return audio / np.max(np.abs(audio))

def resample_to_16k(audio, sr):
    duration = len(audio) / sr
    new_len = int(duration * 16000)
    return resample(audio, new_len), 16000

def transcribe(audio, sr):
    rec = KaldiRecognizer(model, sr)
    audio_bytes = (audio * 32767).astype("int16").tobytes()
    rec.AcceptWaveform(audio_bytes)
    result = rec.FinalResult()
    return json.loads(result).get("text", "")