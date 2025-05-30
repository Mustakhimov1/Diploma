import time
import io
import numpy as np
import soundfile as sf
from crypto_utils import decrypt_audio
from db import conn, cur, insert_processed, insert_asr
from ml_utils import distort, normalize, resample_to_16k, transcribe

print("🟢 DECRYPT_AND_PROCESS ЗАПУЩЕН")
def process_encrypted():
    print("🔁 Processor запущен...")
    time.sleep(5)
    while True:
        try:
            cur.execute("""
                SELECT r.id, r.raw_audio
                FROM audio_raw r
                LEFT JOIN audio_processed p ON r.id = p.id
                WHERE r.is_encrypted = TRUE
                  AND p.id IS NULL
                  AND r.timestamp < now() - interval '2 seconds'
            """)
            rows = cur.fetchall()
            print(f"[info] Найдено {len(rows)} аудио для обработки")

            if not rows:
                time.sleep(5)
                continue

            for audio_id, enc_data in rows:
                try:
                    print(f"[>] Обрабатываю {audio_id}")
                    raw_bytes = decrypt_audio(enc_data)
                    print(f"[AUDIO DEBUG] decrypted bytes: {len(raw_bytes)}")

                    audio_array, orig_sr = sf.read(io.BytesIO(raw_bytes), dtype='int16')
                    normalized = audio_array
                    resampled, sr = resample_to_16k(normalized, orig_sr)

                    resampled = resampled / np.max(np.abs(resampled))
                    print(f"[AUDIO DEBUG] resampled length: {len(resampled)}, max: {np.max(resampled):.4f}")

                    distorted_bytes = (normalized * 32767).astype(np.int16).tobytes()
                    resampled_bytes = (resampled * 32767).astype(np.int16).tobytes()

                    insert_processed(audio_id, distorted_bytes, resampled_bytes)

                    text = transcribe(resampled, sr)
                    insert_asr(audio_id, text)

                    print(f"[✓] Обработано {audio_id} → '{text}'")
                except Exception as e:
                    print(f"[ERROR] Ошибка при обработке {audio_id}: {e}")
        except Exception as e:
            print(f"[DB ERROR] {e}")
            conn.rollback()
            time.sleep(5)

if __name__ == "__main__":
    process_encrypted()