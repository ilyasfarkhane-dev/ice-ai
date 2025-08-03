from typing import Dict, List, Optional
import os
import uuid
import shutil
import logging
from datetime import datetime
from fastapi import UploadFile, HTTPException, BackgroundTasks

from models.CombinedVideoModel import CombinedVideoModel
from services.VideoProcessingService import VideoProcessingService

logger = logging.getLogger(__name__)

class CombinedVideoController:
    """Controller for combined video processing (face extraction + speech transcription)"""
    
    def __init__(self, upload_dir: str = "/home/farkhane/mini-rag/src/assets/videos"):
        self.upload_dir = upload_dir
        self.video_model = CombinedVideoModel()
        self.video_service = VideoProcessingService()
        
        # Create upload directory
        os.makedirs(upload_dir, exist_ok=True)
    
    async def initialize(self):
        """Initialize database connection"""
        await self.video_model.connect()
    
    async def upload_video(self, background_tasks: BackgroundTasks, file: UploadFile) -> Dict:
        """Upload video and start processing"""
        try:
            # Validate file type
            if not file.content_type.startswith('video/'):
                raise HTTPException(status_code=400, detail="File must be a video")
            
            # Generate unique identifiers
            video_id = str(uuid.uuid4())
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{video_id}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            logger.info(f"Starting upload for video: {file.filename} (ID: {video_id})")
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            logger.info(f"File saved successfully: {file_path} ({os.path.getsize(file_path)} bytes)")
            
            # Create video record
            video_record = {
                "video_id": video_id,
                "filename": file.filename,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "upload_time": datetime.now().isoformat(),
                "status": "uploaded",
                "face_extraction": {"status": "queued"},
                "speech_transcription": {"status": "queued"}
            }
            
            # Save to database
            await self.video_model.create_video(video_record)
            
            # Start background processing
            background_tasks.add_task(self._process_video_complete, video_id, file_path)
            
            logger.info(f"Background processing queued for video: {video_id}")
            
            # Return immediate response
            return {
                "message": "Video uploaded successfully! Processing started in background.",
                "video_id": video_id,
                "filename": file.filename,
                "status": "uploaded",
                "file_size_mb": round(os.path.getsize(file_path) / 1024 / 1024, 2),
                "processing": {
                    "face_extraction": "queued",
                    "speech_transcription": "queued"
                },
                "next_steps": {
                    "check_status": f"GET /status/{video_id}",
                    "get_transcription": f"GET /transcription/{video_id}",
                    "get_frames": f"GET /frames/{video_id}"
                }
            }
            
        except Exception as e:
            logger.error(f"Upload error: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def get_video_status(self, video_id: str) -> Dict:
        """Get processing status for a video"""
        video_data = await self.video_model.get_video(video_id)
        
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        return {
            "video_id": video_id,
            "filename": video_data["filename"],
            "status": video_data["status"],
            "upload_time": video_data["upload_time"],
            "face_extraction": video_data["face_extraction"],
            "speech_transcription": video_data["speech_transcription"]
        }
    
    async def get_transcription(self, video_id: str) -> Dict:
        """Get speech transcription with timestamps"""
        video_data = await self.video_model.get_video(video_id)
        
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        speech_data = video_data["speech_transcription"]
        
        if speech_data["status"] != "completed":
            return {
                "video_id": video_id,
                "status": speech_data["status"],
                "message": "Transcription not completed yet"
            }
        
        return {
            "video_id": video_id,
            "transcription_segments": speech_data["transcription_segments"],
            "formatted_transcription": speech_data["formatted_transcription"],
            "total_segments": speech_data["total_segments"],
            "total_duration": speech_data["total_duration"],
            "overall_confidence": speech_data["overall_confidence"],
            "overall_confidence_percentage": speech_data["overall_confidence_percentage"],
            "overall_confidence_quality": speech_data["overall_confidence_quality"],
            "audio_file_path": speech_data["audio_file_path"]
        }
    
    async def get_frames_info(self, video_id: str) -> Dict:
        """Get face extraction information"""
        video_data = await self.video_model.get_video(video_id)
        
        if not video_data:
            raise HTTPException(status_code=404, detail="Video not found")
        
        face_data = video_data["face_extraction"]
        
        if face_data["status"] != "completed":
            return {
                "video_id": video_id,
                "status": face_data["status"],
                "message": "Face extraction not completed yet"
            }
        
        return {
            "video_id": video_id,
            "total_frames": face_data["total_frames"],
            "processed_frames": face_data["processed_frames"],
            "faces_detected": face_data["faces_detected"],
            "frames_directory": face_data["frames_dir"]
        }
    
    async def list_videos(self) -> Dict:
        """List all processed videos"""
        try:
            videos = await self.video_model.get_all_videos()
            
            return {
                "total_videos": len(videos),
                "videos": [
                    {
                        "video_id": video.get("video_id", "unknown"),
                        "filename": video.get("filename", "unknown"),
                        "status": video.get("status", "unknown"),
                        "upload_time": video.get("upload_time", "unknown")
                    }
                    for video in videos if isinstance(video, dict)
                ]
            }
        except Exception as e:
            logger.error(f"Error listing videos: {e}")
            return {
                "total_videos": 0,
                "videos": [],
                "error": str(e)
            }
    
    async def _process_video_complete(self, video_id: str, file_path: str):
        """Background processing for both face extraction and speech transcription"""
        try:
            logger.info(f"Starting background processing for video {video_id}")
            
            # Update status to processing
            await self.video_model.update_video(video_id, {
                "status": "processing",
                "face_extraction.status": "processing",
                "speech_transcription.status": "processing"
            })
            
            logger.info(f"Updated status to processing for video {video_id}")
            
            # Process faces first (usually faster)
            logger.info(f"Starting face extraction for video {video_id}")
            face_result = self.video_service.extract_faces(file_path, video_id)
            
            if face_result["success"]:
                face_data = {
                    "face_extraction": {
                        "status": "completed",
                        "total_frames": face_result["total_frames"],
                        "processed_frames": face_result["processed_frames"],
                        "faces_detected": face_result["faces_detected"],
                        "frames_dir": face_result["frames_dir"],
                        "completed_at": datetime.now().isoformat()
                    }
                }
                await self.video_model.update_video(video_id, face_data)
                logger.info(f"Face extraction completed for video {video_id}: {face_result['faces_detected']} faces found")
            else:
                face_data = {
                    "face_extraction": {
                        "status": "failed",
                        "error": face_result["error"],
                        "failed_at": datetime.now().isoformat()
                    }
                }
                await self.video_model.update_video(video_id, face_data)
                logger.error(f"Face extraction failed for video {video_id}: {face_result['error']}")
            
            # Process speech transcription
            logger.info(f"Starting speech transcription for video {video_id}")
            speech_result = self.video_service.extract_and_transcribe_speech(file_path, video_id)
            
            if speech_result["success"]:
                speech_data = {
                    "speech_transcription": {
                        "status": "completed",
                        "audio_file_path": speech_result["audio_file_path"],
                        "transcription_segments": speech_result["transcription_segments"],
                        "formatted_transcription": speech_result["formatted_transcription"],
                        "total_segments": speech_result["total_segments"],
                        "total_duration": speech_result["total_duration"],
                        "overall_confidence": speech_result["overall_confidence"],
                        "overall_confidence_percentage": speech_result["overall_confidence_percentage"],
                        "overall_confidence_quality": speech_result["overall_confidence_quality"],
                        "completed_at": datetime.now().isoformat()
                    }
                }
                await self.video_model.update_video(video_id, speech_data)
                logger.info(f"Speech transcription completed for video {video_id}: {speech_result['total_segments']} segments")
            else:
                speech_data = {
                    "speech_transcription": {
                        "status": "failed",
                        "error": speech_result["error"],
                        "failed_at": datetime.now().isoformat()
                    }
                }
                await self.video_model.update_video(video_id, speech_data)
                logger.error(f"Speech transcription failed for video {video_id}: {speech_result['error']}")
            
            # Update overall status
            video_data = await self.video_model.get_video(video_id)
            if video_data:
                face_status = video_data["face_extraction"]["status"]
                speech_status = video_data["speech_transcription"]["status"]
                
                if face_status == "completed" and speech_status == "completed":
                    final_update = {
                        "status": "completed",
                        "completed_at": datetime.now().isoformat()
                    }
                    await self.video_model.update_video(video_id, final_update)
                    logger.info(f"All processing completed successfully for video {video_id}")
                elif face_status == "failed" and speech_status == "failed":
                    final_update = {
                        "status": "failed",
                        "failed_at": datetime.now().isoformat()
                    }
                    await self.video_model.update_video(video_id, final_update)
                    logger.error(f"All processing failed for video {video_id}")
                else:
                    final_update = {
                        "status": "partial_success",
                        "partial_completed_at": datetime.now().isoformat()
                    }
                    await self.video_model.update_video(video_id, final_update)
                    logger.warning(f"Partial processing completed for video {video_id}")
            
        except Exception as e:
            logger.error(f"Unexpected error in background processing for video {video_id}: {e}")
            error_update = {
                "status": "failed",
                "error": str(e),
                "failed_at": datetime.now().isoformat()
            }
            await self.video_model.update_video(video_id, error_update)
