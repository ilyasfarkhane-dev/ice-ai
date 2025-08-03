from typing import Dict, List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends

from controllers.CombinedVideoController import CombinedVideoController

# Create router
video_router = APIRouter(prefix="/video", tags=["Combined Video Processing"])

# Initialize controller
video_controller = CombinedVideoController()

async def get_video_controller():
    """Dependency to get the video controller with initialized connection"""
    await video_controller.initialize()
    return video_controller

@video_router.post("/upload", response_model=Dict)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    controller: CombinedVideoController = Depends(get_video_controller)
):
    """
    Upload a video file for combined processing (face extraction + speech transcription)
    
    - **file**: Video file to process
    - Returns: Video ID and processing status
    """
    return await controller.upload_video(background_tasks, file)

@video_router.get("/status/{video_id}", response_model=Dict)
async def get_video_status(
    video_id: str,
    controller: CombinedVideoController = Depends(get_video_controller)
):
    """
    Get processing status for a specific video
    
    - **video_id**: Unique video identifier
    - Returns: Processing status for face extraction and speech transcription
    """
    return await controller.get_video_status(video_id)

@video_router.get("/transcription/{video_id}", response_model=Dict)
async def get_transcription(
    video_id: str,
    controller: CombinedVideoController = Depends(get_video_controller)
):
    """
    Get speech transcription with timestamps and confidence scores
    
    - **video_id**: Unique video identifier  
    - Returns: Transcription segments, overall confidence, and quality metrics
    """
    return await controller.get_transcription(video_id)

@video_router.get("/frames/{video_id}", response_model=Dict)
async def get_frames_info(
    video_id: str,
    controller: CombinedVideoController = Depends(get_video_controller)
):
    """
    Get face extraction information
    
    - **video_id**: Unique video identifier
    - Returns: Frame processing details and face detection results
    """
    return await controller.get_frames_info(video_id)

@video_router.get("/list", response_model=Dict)
async def list_videos(
    controller: CombinedVideoController = Depends(get_video_controller)
):
    """
    List all processed videos
    
    - Returns: Summary of all videos with their processing status
    """
    return await controller.list_videos()

# Additional useful endpoints

@video_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "combined_video_processing"}

@video_router.get("/info")
async def get_service_info():
    """Get service information"""
    return {
        "service": "Combined Video Processing API",
        "version": "1.0.0",
        "capabilities": [
            "Face extraction from video frames",
            "Speech transcription with confidence scores",
            "MongoDB persistent storage",
            "Background processing",
            "Confidence percentage calculation",
            "Quality rating system"
        ],
        "supported_formats": ["mp4", "avi", "mov", "mkv"],
        "features": {
            "face_detection": "OpenCV-based face extraction",
            "speech_transcription": "Whisper-based with confidence scoring",
            "storage": "MongoDB with in-memory fallback",
            "processing": "Asynchronous background tasks"
        }
    }
