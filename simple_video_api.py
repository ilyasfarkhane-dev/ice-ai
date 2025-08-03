from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import uuid
from typing import Dict, Any

app = FastAPI(title="Video Processing API - Simplified")

# Simple upload directory
UPLOAD_DIR = "/home/farkhane/mini-rag/src/assets/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
async def health_check():
    return {
        "status": "running", 
        "message": "Video Processing API - Simplified Version",
        "endpoints": [
            "POST /upload - Upload video",
            "GET /status/{video_id} - Get status", 
            "GET /test - Test endpoint"
        ]
    }

@app.get("/test")
async def test_endpoint():
    return {"test": "working", "mongodb": "not connected yet", "speech": "simplified"}

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Simple video upload without processing"""
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        video_id = str(uuid.uuid4())
        
        return {
            "message": "Video uploaded successfully",
            "video_id": video_id,
            "filename": file.filename,
            "file_path": file_path,
            "status": "uploaded"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload error: {str(e)}")

@app.get("/status/{video_id}")
async def get_status(video_id: str):
    """Simple status check"""
    return {
        "video_id": video_id,
        "status": "uploaded",
        "message": "Simplified API - no processing yet"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
