from fastapi import FastAPI, HTTPException
import subprocess, os
from subprocess import Popen

app = FastAPI()

@app.post("/run_processor")
def run_processor():
    try:
        script_path = os.path.join(os.path.dirname(__file__), "decrypt_and_process.py")
        print(f"[INFO] Запуск: {script_path}")
        process = Popen(["python", script_path])
        return {"status": "processing started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))