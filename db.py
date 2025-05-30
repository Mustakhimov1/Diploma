import psycopg2
import uuid, os

conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME", "audio_db"),
    user=os.getenv("DB_USER", "audio_user"),
    password=os.getenv("DB_PASS", "audio_pass"),
    host=os.getenv("DB_HOST", "localhost"),
    port="5432"
)
cur = conn.cursor()

def insert_encrypted_audio(device_id, encrypted_audio):
    audio_id = str(uuid.uuid4())
    try:
        conn.rollback()
        cur.execute(
            "INSERT INTO audio_raw (id, device_id, timestamp, raw_audio, is_encrypted) VALUES (%s, %s, now(), %s, %s)",
            (audio_id, device_id, encrypted_audio, True)
        )
        conn.commit()
        return audio_id
    except Exception as e:
        conn.rollback()
        raise e

def insert_processed(audio_id, distorted, normalized):
    cur.execute("""
        INSERT INTO audio_processed (id, distorted_audio, normalized_audio)
        VALUES (%s, %s, %s)
    """, (audio_id, psycopg2.Binary(distorted), psycopg2.Binary(normalized)))
    conn.commit()

def insert_asr(audio_id, text):
    cur.execute("""
        INSERT INTO asr_results (id, transcribed_text, confidence, model_version)
        VALUES (%s, %s, %s, %s)
    """, (audio_id, text, 0.9, "vosk-ru"))
    conn.commit()