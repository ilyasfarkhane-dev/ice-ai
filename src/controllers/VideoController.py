from fastapi import UploadFile, HTTPException, BackgroundTasks
import os
import shutil
import uuid
import logging
from typing import Optional, Dict, Any
from controllers.BaseController import BaseController
from models.VideoModel import VideoModel, VideoProcessingStatus
from services.VideoFaceExtractor import VideoFaceExtractorService
from services.SpeechTranscriptionService import SpeechTranscriptionService


class VideoController(BaseController):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.video_service = VideoFaceExtractorService()
        self.speech_service = SpeechTranscriptionService()
        self.upload_dir = os.path.join(os.path.dirname(__file__), "../assets/videos")
        os.makedirs(self.upload_dir, exist_ok=True)

    async def upload_video(self, file: UploadFile, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Upload a video file and start processing in background"""
        try:
            # Validate file type
            if not file.content_type.startswith('video/'):
                raise HTTPException(status_code=400, detail="File must be a video")
            
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save uploaded file
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Create video record in database
            video_data = {
                "filename": file.filename,
                "file_path": file_path,
                "file_size": os.path.getsize(file_path),
                "content_type": file.content_type,
                "status": VideoProcessingStatus.UPLOADED.value,
                "frame_interval": 30,  # Default frame interval
                # Speech transcription fields
                "audio_file_path": None,
                "transcription_segments": [],
                "pitch_analysis": [],
                "emotion_classification": [],
                "transcription_status": "pending",
                "transcription_error": None
            }
            
            video_id = await VideoModel.create(video_data)
            
            # Start background processing
            background_tasks.add_task(
                self.process_video_with_speech, 
                str(video_id), 
                file_path
            )
            
            return {
                "message": "Video uploaded successfully",
                "video_id": str(video_id),
                "filename": file.filename,
                "status": "processing_started"
            }
            
        except Exception as e:
            self.logger.error(f"Error uploading video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

    async def get_video_status(self, video_id: str) -> Dict[str, Any]:
        """Get processing status of a video"""
        try:
            video = await VideoModel.get_by_id(video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            # Get frame statistics from MongoDB
            stats = await self.video_service.get_video_stats(video_id)
            
            return {
                "video_id": video_id,
                "filename": video.get("filename"),
                "status": video.get("status"),
                "created_at": video.get("created_at"),
                "processing_stats": stats,
                # Speech transcription status
                "transcription_status": video.get("transcription_status", "pending"),
                "transcription_error": video.get("transcription_error"),
                "audio_file_path": video.get("audio_file_path"),
                "transcription_segments_count": len(video.get("transcription_segments", [])),
                "pitch_analysis_points": len(video.get("pitch_analysis", [])),
                "emotion_classifications": len(video.get("emotion_classification", []))
            }
            
        except Exception as e:
            self.logger.error(f"Error getting video status: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error getting video status: {str(e)}")

    async def list_videos(self, skip: int = 0, limit: int = 10) -> Dict[str, Any]:
        """List all uploaded videos"""
        try:
            videos = await VideoModel.get_all(skip=skip, limit=limit)
            total = await VideoModel.count()
            
            return {
                "videos": videos,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            self.logger.error(f"Error listing videos: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error listing videos: {str(e)}")

    async def delete_video(self, video_id: str) -> Dict[str, Any]:
        """Delete a video and its associated data"""
        try:
            video = await VideoModel.get_by_id(video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            # Delete video file
            file_path = video.get("file_path")
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete associated frames and faces
            await self.video_service.cleanup_video_data(video_id)
            
            # Delete video record
            await VideoModel.delete(video_id)
            
            return {
                "message": "Video deleted successfully",
                "video_id": video_id
            }
            
        except Exception as e:
            self.logger.error(f"Error deleting video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting video: {str(e)}")

    async def reprocess_video(self, video_id: str, frame_interval: Optional[int] = None, background_tasks: BackgroundTasks = None) -> Dict[str, Any]:
        """Reprocess a video with different settings"""
        try:
            video = await VideoModel.get_by_id(video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            file_path = video.get("file_path")
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Video file not found")
            
            # Update frame interval if provided
            if frame_interval:
                await VideoModel.update(video_id, {"frame_interval": frame_interval})
            
            # Update status to processing
            await VideoModel.update(video_id, {"status": VideoProcessingStatus.PROCESSING.value})
            
            # Clean up old data
            await self.video_service.cleanup_video_data(video_id)
            
            # Start reprocessing
            if background_tasks:
                background_tasks.add_task(
                    self.process_video_with_speech, 
                    video_id, 
                    file_path,
                    frame_interval or video.get("frame_interval", 30)
                )
            
            return {
                "message": "Video reprocessing started",
                "video_id": video_id,
                "frame_interval": frame_interval or video.get("frame_interval", 30)
            }
            
        except Exception as e:
            self.logger.error(f"Error reprocessing video: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reprocessing video: {str(e)}")

    async def process_video_with_speech(self, video_id: str, file_path: str, frame_interval: int = 30):
        """Process video with both face extraction and speech transcription"""
        try:
            self.logger.info(f"Starting combined processing for video {video_id}")
            
            # Update status to processing
            await VideoModel.update(video_id, {
                "status": VideoProcessingStatus.PROCESSING.value,
                "transcription_status": "processing"
            })
            
            # Process video faces (existing functionality)
            await self.video_service.process_video_async(video_id, file_path, frame_interval)
            
            # Process speech transcription
            try:
                # Extract audio from video
                audio_path = self.speech_service.extract_audio(file_path, video_id)
                
                # Update audio path in database
                await VideoModel.update(video_id, {"audio_file_path": audio_path})
                
                # Transcribe speech with timestamps
                transcription_segments = self.speech_service.transcribe_with_timestamps(audio_path, video_id)
                
                # Analyze pitch
                pitch_analysis = self.speech_service.analyze_pitch(audio_path)
                
                # Classify emotions
                emotion_classification = self.speech_service.classify_emotion(transcription_segments, pitch_analysis)
                
                # Update database with speech analysis results
                await VideoModel.update(video_id, {
                    "transcription_segments": transcription_segments,
                    "pitch_analysis": pitch_analysis,
                    "emotion_classification": emotion_classification,
                    "transcription_status": "completed"
                })
                
                self.logger.info(f"Speech transcription completed for video {video_id}")
                
            except Exception as speech_error:
                self.logger.error(f"Speech processing failed for video {video_id}: {str(speech_error)}")
                await VideoModel.update(video_id, {
                    "transcription_status": "failed",
                    "transcription_error": str(speech_error)
                })
            
            self.logger.info(f"Combined processing completed for video {video_id}")
            
        except Exception as e:
            self.logger.error(f"Error in combined processing for video {video_id}: {str(e)}")
            await VideoModel.update(video_id, {
                "status": VideoProcessingStatus.FAILED.value,
                "transcription_status": "failed",
                "transcription_error": str(e)
            })

    async def transcribe_existing_video(self, video_id: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
        """Start transcription for an existing video without reprocessing faces"""
        try:
            # Get video information
            video = await VideoModel.get_by_id(video_id)
            if not video:
                raise HTTPException(status_code=404, detail="Video not found")
            
            file_path = video.get("file_path")
            if not file_path or not os.path.exists(file_path):
                raise HTTPException(status_code=404, detail="Video file not found")
            
            # Reset transcription status
            await VideoModel.update(video_id, {
                "transcription_status": "pending",
                "transcription_error": None
            })
            
            # Start background transcription
            background_tasks.add_task(
                self.process_speech_only,
                video_id,
                file_path
            )
            
            return {
                "message": "Speech transcription started",
                "video_id": video_id,
                "status": "processing"
            }
            
        except Exception as e:
            self.logger.error(f"Error starting transcription for video {video_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error starting transcription: {str(e)}")

    async def process_speech_only(self, video_id: str, file_path: str):
        """Process only speech transcription for an existing video"""
        try:
            self.logger.info(f"Starting speech-only processing for video {video_id}")
            
            # Update status
            await VideoModel.update(video_id, {"transcription_status": "processing"})
            
            # Extract audio from video
            audio_path = self.speech_service.extract_audio(file_path, video_id)
            
            # Update audio path in database
            await VideoModel.update(video_id, {"audio_file_path": audio_path})
            
            # Transcribe speech with timestamps
            transcription_segments = self.speech_service.transcribe_with_timestamps(audio_path, video_id)
            
            # Analyze pitch
            pitch_analysis = self.speech_service.analyze_pitch(audio_path)
            
            # Classify emotions
            emotion_classification = self.speech_service.classify_emotion(transcription_segments, pitch_analysis)
            
            # Update database with speech analysis results
            await VideoModel.update(video_id, {
                "transcription_segments": transcription_segments,
                "pitch_analysis": pitch_analysis,
                "emotion_classification": emotion_classification,
                "transcription_status": "completed"
            })
            
            self.logger.info(f"Speech-only processing completed for video {video_id}")
            
        except Exception as e:
            self.logger.error(f"Speech-only processing failed for video {video_id}: {str(e)}")
            await VideoModel.update(video_id, {
                "transcription_status": "failed",
                "transcription_error": str(e)
            })
