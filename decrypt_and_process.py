import time
import io
import numpy as np
import soundfile as sf
from crypto_utils import decrypt_audio
from db import conn, cur, insert_processed, insert_asr
from ml_utils import distort, normalize, resample_to_16k, transcribe

def process_encrypted():
    print("Processor is up")
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
            print(f"Found {len(rows)} audio files to process")

            if not rows:
                time.sleep(5)
                continue

            for audio_id, enc_data in rows:
                try:
                    print(f"Processing {audio_id}")
                    raw_bytes = decrypt_audio(enc_data)
                    print(f"decrypted bytes: {len(raw_bytes)}")

                    audio_array, orig_sr = sf.read(io.BytesIO(raw_bytes), dtype='int16')
                    normalized = audio_array
                    resampled, sr = resample_to_16k(normalized, orig_sr)

                    resampled = resampled / np.max(np.abs(resampled))
                    print(f"resampled length: {len(resampled)}, max: {np.max(resampled):.4f}")

                    distorted_bytes = (normalized * 32767).astype(np.int16).tobytes()
                    resampled_bytes = (resampled * 32767).astype(np.int16).tobytes()

                    insert_processed(audio_id, distorted_bytes, resampled_bytes)

                    text = transcribe(resampled, sr)
                    insert_asr(audio_id, text)

                    print(f"Processed {audio_id} → '{text}'")
                except Exception as e:
                    print(f"Error processing {audio_id}: {e}")
        except Exception as e:
            print(f"DB ERROR {e}")
            conn.rollback()
            time.sleep(5)

if __name__ == "__main__":
    process_encrypted()