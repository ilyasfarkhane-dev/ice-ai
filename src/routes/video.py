from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Query
from typing import Optional
from controllers.VideoController import VideoController
from models.VideoModel import VideoModel

router = APIRouter(prefix="/api/videos", tags=["Videos"])
video_controller = VideoController()

@router.post("/upload")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Video file to upload")
):
    """
    Upload a video file for face extraction processing
    
    - **file**: Video file (mp4, avi, mov, etc.)
    
    Returns video ID and processing status
    """
    return await video_controller.upload_video(file, background_tasks)

@router.get("/{video_id}/status")
async def get_video_status(video_id: str):
    """
    Get processing status and statistics for a video
    
    - **video_id**: ID of the uploaded video
    
    Returns current processing status and frame/face statistics
    """
    return await video_controller.get_video_status(video_id)

@router.get("/")
async def list_videos(
    skip: int = Query(0, ge=0, description="Number of videos to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of videos to return")
):
    """
    List all uploaded videos with pagination
    
    - **skip**: Number of videos to skip (for pagination)
    - **limit**: Maximum number of videos to return (1-100)
    
    Returns list of videos with their status and metadata
    """
    return await video_controller.list_videos(skip, limit)

@router.delete("/{video_id}")
async def delete_video(video_id: str):
    """
    Delete a video and all its associated data
    
    - **video_id**: ID of the video to delete
    
    Removes video file, extracted frames, faces, and database records
    """
    return await video_controller.delete_video(video_id)

@router.post("/{video_id}/reprocess")
async def reprocess_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    frame_interval: Optional[int] = Query(None, ge=1, le=120, description="Frame extraction interval (1-120)")
):
    """
    Reprocess a video with different settings
    
    - **video_id**: ID of the video to reprocess
    - **frame_interval**: New frame extraction interval (optional)
    
    Clears existing data and starts reprocessing with new settings
    """
    return await video_controller.reprocess_video(video_id, frame_interval, background_tasks)

@router.get("/{video_id}/frames")
async def get_video_frames(
    video_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    faces_only: bool = Query(False, description="Return only frames with detected faces")
):
    """
    Get extracted frames for a video
    
    - **video_id**: ID of the video
    - **skip**: Number of frames to skip
    - **limit**: Maximum number of frames to return
    - **faces_only**: If true, returns only frames where faces were detected
    
    Returns list of frame metadata including paths to frame and face images
    """
    try:
        from services.VideoFaceExtractor import VideoFaceExtractorService
        service = VideoFaceExtractorService()
        
        frames_collection = await service.get_frames_collection()
        
        # Build query
        query = {"video_id": video_id}
        if faces_only:
            query["face_found"] = True
        
        # Get frames with pagination
        cursor = frames_collection.find(query).skip(skip).limit(limit).sort("frame_number", 1)
        frames = await cursor.to_list(length=None)
        
        # Convert ObjectId to string
        for frame in frames:
            frame["_id"] = str(frame["_id"])
        
        # Get total count
        total = await frames_collection.count_documents(query)
        
        return {
            "frames": frames,
            "total": total,
            "skip": skip,
            "limit": limit,
            "faces_only": faces_only
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving frames: {str(e)}")

@router.get("/{video_id}/download-frames")
async def download_frames_zip(video_id: str, faces_only: bool = Query(False)):
    """
    Download all frames as a ZIP file
    
    - **video_id**: ID of the video
    - **faces_only**: If true, downloads only cropped face images
    
    Returns ZIP file containing all frame images
    """
    try:
        import os
        import zipfile
        from fastapi.responses import FileResponse
        import tempfile
        
        from services.VideoFaceExtractor import VideoFaceExtractorService
        service = VideoFaceExtractorService()
        
        # Get video info
        video = await VideoModel.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        # Get frames
        frames_collection = await service.get_frames_collection()
        query = {"video_id": video_id}
        if faces_only:
            query["face_found"] = True
            
        frames = await frames_collection.find(query).to_list(length=None)
        
        # Create temporary ZIP file
        temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
        
        with zipfile.ZipFile(temp_zip.name, 'w') as zip_file:
            for frame in frames:
                if faces_only and frame.get("face_path") and os.path.exists(frame["face_path"]):
                    zip_file.write(frame["face_path"], os.path.basename(frame["face_path"]))
                elif not faces_only and frame.get("frame_path") and os.path.exists(frame["frame_path"]):
                    zip_file.write(frame["frame_path"], os.path.basename(frame["frame_path"]))
        
        filename = f"video_{video_id}_{'faces' if faces_only else 'frames'}.zip"
        
        return FileResponse(
            temp_zip.name, 
            media_type='application/zip',
            filename=filename,
            background=BackgroundTasks()  # Clean up temp file
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating ZIP file: {str(e)}")


@router.get("/transcription/{video_id}")
async def get_transcription(video_id: str):
    """
    Get speech transcription with timestamps for a video
    
    Returns transcription segments with timestamps like:
    [5.72s - 7.78s]: Can I come in, ma'am?
    """
    try:
        video = await VideoModel.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "video_id": video_id,
            "transcription_status": video.get("transcription_status", "pending"),
            "transcription_segments": video.get("transcription_segments", []),
            "transcription_error": video.get("transcription_error"),
            "formatted_transcription": format_transcription_display(video.get("transcription_segments", []))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting transcription: {str(e)}")


@router.get("/pitch-analysis/{video_id}")
async def get_pitch_analysis(video_id: str):
    """
    Get pitch analysis data for a video
    
    Returns pitch analysis with emotional classification
    """
    try:
        video = await VideoModel.get_by_id(video_id)
        if not video:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "video_id": video_id,
            "pitch_analysis": video.get("pitch_analysis", []),
            "emotion_classification": video.get("emotion_classification", []),
            "transcription_status": video.get("transcription_status", "pending")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pitch analysis: {str(e)}")


@router.post("/transcribe-only/{video_id}")
async def transcribe_only(video_id: str, background_tasks: BackgroundTasks):
    """
    Start transcription processing for an existing video (without reprocessing faces)
    """
    try:
        controller = VideoController()
        result = await controller.transcribe_existing_video(video_id, background_tasks)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting transcription: {str(e)}")


def format_transcription_display(segments: list) -> list:
    """Format transcription segments for display like [5.72s - 7.78s]: Can I come in, ma'am?"""
    formatted = []
    for segment in segments:
        start_time = segment.get("start_time", 0)
        end_time = segment.get("end_time", 0)
        text = segment.get("text", "")
        
        formatted_segment = f"[{start_time:.2f}s - {end_time:.2f}s]: {text}"
        formatted.append(formatted_segment)
    
    return formatted
