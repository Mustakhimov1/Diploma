import numpy as np
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, HTMLResponse
from db import conn, cur
from threading import Timer
import requests, io, soundfile as sf

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    cur.execute("""
        SELECT a.id, a.device_id, a.timestamp, r.transcribed_text
        FROM asr_results r
        JOIN audio_raw a ON a.id = r.id
        ORDER BY a.timestamp DESC
        LIMIT 20
    """)
    rows = cur.fetchall()
    results = [{
        "id": str(row[0]),
        "device": row[1],
        "time": row[2].strftime("%Y-%m-%d %H:%M:%S"),
        "text": row[3]
    } for row in rows]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "results": results
    })

@app.get("/audio/{audio_id}.wav")
def get_audio(audio_id: str):
    cur.execute("SELECT normalized_audio FROM audio_processed WHERE id = %s", (audio_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Audio not found")
    return Response(content=row[0], media_type="audio/wav")

@app.get("/audio/distorted/{audio_id}.wav")
def get_distorted_audio(audio_id: str):
    cur.execute("SELECT distorted_audio FROM audio_processed WHERE id = %s", (audio_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Distorted audio not found")

    buf = io.BytesIO()
    audio = np.frombuffer(row[0], dtype=np.int16)
    sf.write(buf, audio, 16000, format='WAV')
    buf.seek(0)
    return Response(content=buf.read(), media_type="audio/wav")

@app.get("/audio/normalized/{audio_id}.wav")
def get_normalized_audio(audio_id: str):
    cur.execute("SELECT normalized_audio FROM audio_processed WHERE id = %s", (audio_id,))
    row = cur.fetchone()
    if row:
        buf = io.BytesIO()
        audio = np.frombuffer(row[0], dtype=np.int16)
        sf.write(buf, audio, 16000, format='WAV')
        buf.seek(0)
        return Response(content=buf.read(), media_type="audio/wav")
    raise HTTPException(status_code=404, detail="Normalized audio not found")

@app.get("/asr_results")
def get_results():
    try:
        cur.execute("SELECT id, transcribed_text FROM asr_results ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()
        return [{"id": str(row[0]), "text": row[1]} for row in rows]
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@app.get("/raw_audio")
def get_raw():
    try:
        cur.execute("SELECT id, device_id, timestamp FROM audio_raw ORDER BY timestamp DESC LIMIT 10")
        rows = cur.fetchall()
        return [{"id": str(r[0]), "device": r[1], "time": r[2].isoformat()} for r in rows]
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.post("/run_processor")
def trigger_processing():
    try:
        response = requests.post("http://processor:9000/run_processor")
        return {"status": response.json()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))