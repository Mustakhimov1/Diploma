from fastapi import FastAPI, UploadFile, File, HTTPException
from db import insert_encrypted_audio
from crypto_utils import encrypt_audio
import requests

app = FastAPI()

@app.post("/upload-audio")
async def upload_audio(device_id: str, file: UploadFile = File(...)):
    try:
        data = await file.read()
        encrypted = encrypt_audio(data)
        audio_id = insert_encrypted_audio(device_id, encrypted)
        return {"status": "received", "audio_id": str(audio_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trigger-processor")
def trigger():
    try:
        res = requests.post("http://processor:9000/run")
        return res.json()
    except Exception as e:
        return {"error": str(e)}