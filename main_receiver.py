import soundfile as sf
from crypto_utils import encrypt_audio
from db import insert_encrypted_audio

def receive_audio_from_esp32(file_path='esp_audio.wav', device_id='esp32_mic1'):
    audio_data, sr, _ = sf.read(file_path)
    print(f"[RECEIVER] Audio SR: {sr}")
    audio_bytes = (audio_data * 32767).astype("int16").tobytes()
    encrypted = encrypt_audio(audio_bytes)
    audio_id = insert_encrypted_audio(device_id, encrypted)
    print(f"Saved encrypted audio with id {audio_id}")

if __name__ == '__main__':
    receive_audio_from_esp32()