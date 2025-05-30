CREATE TABLE IF NOT EXISTS audio_raw (
    id UUID PRIMARY KEY,
    device_id TEXT,
    timestamp TIMESTAMP,
    raw_audio BYTEA,
    is_encrypted BOOLEAN
);

CREATE TABLE IF NOT EXISTS audio_processed (
    id UUID PRIMARY KEY,
    distorted_audio BYTEA,
    normalized_audio BYTEA
);

CREATE TABLE IF NOT EXISTS asr_results (
    id UUID PRIMARY KEY,
    transcribed_text TEXT,
    confidence REAL,
    model_version TEXT,
    created_at TIMESTAMP DEFAULT now()
);