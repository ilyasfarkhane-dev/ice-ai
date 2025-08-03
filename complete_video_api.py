from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
import os
import shutil
import uuid
import logging
from typing import Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Video Processing API - Face + Speech", version="1.0.0")

# MongoDB Configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "video_faces"
COLLECTION_NAME = "processed_videos"  # New collection for this API

# MongoDB connection
client = None
database = None
collection = None

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, database, collection
    try:
        client = AsyncIOMotorClient(MONGODB_URL)
        database = client[DATABASE_NAME]
        collection = database[COLLECTION_NAME]
        # Test connection
        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB at {MONGODB_URL}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        logger.info("Falling back to in-memory storage")
        return False

# Initialize MongoDB connection
mongo_connected = False

@app.on_event("startup")
async def startup_event():
    global mongo_connected
    mongo_connected = await connect_to_mongo()

# Directories
BASE_DIR = "/home/farkhane/mini-rag/src/assets"
UPLOAD_DIR = f"{BASE_DIR}/videos"
FRAMES_DIR = f"{BASE_DIR}/frames"
AUDIO_DIR = f"{BASE_DIR}/audio"

# Create directories
for dir_path in [UPLOAD_DIR, FRAMES_DIR, AUDIO_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# Fallback in-memory storage for when MongoDB is not available
video_database = {}

# Database helper functions
async def save_video_to_db(video_data: Dict) -> bool:
    """Save video data to MongoDB or fallback to in-memory"""
    try:
        if mongo_connected and collection is not None:
            # Save to MongoDB
            result = await collection.insert_one(video_data)
            logger.info(f"Video {video_data['video_id']} saved to MongoDB")
            return True
        else:
            # Fallback to in-memory
            video_database[video_data['video_id']] = video_data
            logger.info(f"Video {video_data['video_id']} saved to in-memory storage")
            return True
    except Exception as e:
        logger.error(f"Failed to save video to database: {e}")
        # Fallback to in-memory even if MongoDB fails
        video_database[video_data['video_id']] = video_data
        return True

async def get_video_from_db(video_id: str) -> Dict:
    """Get video data from MongoDB or fallback to in-memory"""
    try:
        if mongo_connected and collection is not None:
            # Get from MongoDB
            video_data = await collection.find_one({"video_id": video_id})
            if video_data:
                # Remove MongoDB's _id field
                video_data.pop('_id', None)
                return video_data
        
        # Fallback to in-memory
        return video_database.get(video_id)
    except Exception as e:
        logger.error(f"Failed to get video from database: {e}")
        # Fallback to in-memory
        return video_database.get(video_id)

async def update_video_in_db(video_id: str, update_data: Dict) -> bool:
    """Update video data in MongoDB or fallback to in-memory"""
    try:
        if mongo_connected and collection is not None:
            # Update in MongoDB
            result = await collection.update_one(
                {"video_id": video_id}, 
                {"$set": update_data}
            )
            if result.modified_count > 0:
                logger.info(f"Video {video_id} updated in MongoDB")
                return True
        
        # Fallback to in-memory
        if video_id in video_database:
            video_database[video_id].update(update_data)
            logger.info(f"Video {video_id} updated in in-memory storage")
            return True
        return False
    except Exception as e:
        logger.error(f"Failed to update video in database: {e}")
        # Fallback to in-memory
        if video_id in video_database:
            video_database[video_id].update(update_data)
            return True
        return False

async def get_all_videos_from_db() -> List[Dict]:
    """Get all videos from MongoDB or fallback to in-memory"""
    try:
        if mongo_connected and collection is not None:
            # Get from MongoDB
            cursor = collection.find({})
            videos = []
            async for video in cursor:
                video.pop('_id', None)  # Remove MongoDB's _id field
                videos.append(video)
            return videos
        
        # Fallback to in-memory
        return list(video_database.values())
    except Exception as e:
        logger.error(f"Failed to get videos from database: {e}")
        # Fallback to in-memory
        return list(video_database.values())

class VideoProcessor:
    """Combined video and speech processor"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._whisper_model = None  # Lazy loading
    
    def get_whisper_model(self):
        """Load Whisper model only once and reuse it"""
        if self._whisper_model is None:
            self.logger.info("Loading Whisper model (one-time initialization)...")
            import whisper
            self._whisper_model = whisper.load_model("base")
            self.logger.info("Whisper model loaded successfully")
        return self._whisper_model
    
    def extract_faces(self, video_path: str, video_id: str) -> Dict:
        """Extract faces from video frames"""
        try:
            import cv2
            
            self.logger.info(f"Starting face extraction for {video_id}")
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            frames_processed = 0
            faces_found = 0
            frame_interval = 30  # Process every 30th frame
            
            video_frames_dir = os.path.join(FRAMES_DIR, video_id)
            os.makedirs(video_frames_dir, exist_ok=True)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frames_processed % frame_interval == 0:
                    # Convert to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    
                    if len(faces) > 0:
                        faces_found += len(faces)
                        
                        # Save frame with faces
                        frame_filename = f"frame_{frames_processed:06d}.jpg"
                        frame_path = os.path.join(video_frames_dir, frame_filename)
                        cv2.imwrite(frame_path, frame)
                        
                        # Save individual face crops
                        for i, (x, y, w, h) in enumerate(faces):
                            face_crop = frame[y:y+h, x:x+w]
                            face_filename = f"face_{frames_processed:06d}_{i}.jpg"
                            face_path = os.path.join(video_frames_dir, face_filename)
                            cv2.imwrite(face_path, face_crop)
                
                frames_processed += 1
            
            cap.release()
            
            result = {
                "total_frames": total_frames,
                "processed_frames": frames_processed,
                "faces_detected": faces_found,
                "frames_dir": video_frames_dir,
                "success": True
            }
            
            self.logger.info(f"Face extraction completed: {faces_found} faces in {frames_processed} frames")
            return result
            
        except Exception as e:
            self.logger.error(f"Face extraction failed: {e}")
            return {"success": False, "error": str(e)}
    
    def convert_confidence_to_percentage(self, log_prob):
        """Convert Whisper's negative log probability to 0-100% confidence"""
        if log_prob >= 0:
            return 100.0
        # Convert log probability to percentage (empirical mapping)
        # -0.1 ≈ 90%, -0.3 ≈ 74%, -0.5 ≈ 61%, -1.0 ≈ 37%
        percentage = max(0, min(100, 100 * (1 + log_prob / 2.5)))
        return round(percentage, 1)
    
    def get_confidence_quality(self, log_prob):
        """Get human-readable confidence quality"""
        if log_prob >= -0.1:
            return "Excellent"
        elif log_prob >= -0.3:
            return "Good"
        elif log_prob >= -0.5:
            return "Fair"
        elif log_prob >= -1.0:
            return "Poor"
        else:
            return "Very Poor"

    def extract_and_transcribe_speech(self, video_path: str, video_id: str) -> Dict:
        """Extract audio and transcribe speech with timestamps"""
        try:
            self.logger.info(f"Starting speech transcription for {video_id}")
            
            # Import speech processing libraries
            from moviepy.editor import VideoFileClip
            
            # Extract audio
            self.logger.info("Extracting audio...")
            audio_filename = f"video_{video_id}_audio.wav"
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            
            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
            clip.close()
            
            # Get pre-loaded Whisper model (avoids loading delay)
            self.logger.info("Using pre-loaded Whisper model...")
            model = self.get_whisper_model()
            
            # Transcribe with timestamps
            self.logger.info("Transcribing speech...")
            result = model.transcribe(audio_path)
            
            # Format transcription segments
            transcription_segments = []
            formatted_transcription = []
            confidence_scores = []
            
            for segment in result['segments']:
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()
                confidence_raw = segment.get('avg_logprob', 0)
                confidence_percentage = self.convert_confidence_to_percentage(confidence_raw)
                
                transcription_segments.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "text": text,
                    "confidence": confidence_raw,
                    "confidence_percentage": confidence_percentage
                })
                
                formatted_line = f"[{start_time:.2f}s - {end_time:.2f}s]: {text}"
                formatted_transcription.append(formatted_line)
                
                # Collect confidence scores for overall calculation
                confidence_scores.append(confidence_raw)
            
            # Calculate overall confidence score
            overall_confidence_raw = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            overall_confidence_percentage = self.convert_confidence_to_percentage(overall_confidence_raw)
            overall_confidence_quality = self.get_confidence_quality(overall_confidence_raw)
            
            result = {
                "audio_file_path": audio_path,
                "transcription_segments": transcription_segments,
                "formatted_transcription": formatted_transcription,
                "total_segments": len(transcription_segments),
                "total_duration": result['segments'][-1]['end'] if result['segments'] else 0,
                "overall_confidence": overall_confidence_raw,
                "overall_confidence_percentage": overall_confidence_percentage,
                "overall_confidence_quality": overall_confidence_quality,
                "success": True
            }
            
            self.logger.info(f"Speech transcription completed: {len(transcription_segments)} segments")
            return result
            
        except Exception as e:
            self.logger.error(f"Speech transcription failed: {e}")
            return {"success": False, "error": str(e)}

# Global processor instance
processor = VideoProcessor()

@app.get("/")
async def health_check():
    return {
        "status": "running",
        "message": "Video Processing API - Face Extraction + Speech Transcription",
        "features": [
            "Face detection and cropping",
            "Speech transcription with timestamps",
            "Combined processing via Postman upload"
        ],
        "endpoints": {
            "upload": "POST /upload",
            "status": "GET /status/{video_id}",
            "transcription": "GET /transcription/{video_id}",
            "frames": "GET /frames/{video_id}"
        }
    }

@app.post("/upload")
async def upload_video(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Upload video and start both face extraction and speech transcription"""
    try:
        # Validate file type
        if not file.content_type.startswith('video/'):
            raise HTTPException(status_code=400, detail="File must be a video")
        
        # Generate unique identifiers
        video_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{video_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
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
            "status": "uploaded",  # Changed from "processing" to "uploaded"
            "face_extraction": {"status": "queued"},  # Changed from "pending" to "queued"
            "speech_transcription": {"status": "queued"}  # Changed from "pending" to "queued"
        }
        
        # Save to database (MongoDB or in-memory fallback)
        await save_video_to_db(video_record)
        
        # Start background processing (this runs asynchronously)
        background_tasks.add_task(process_video_complete, video_id, file_path)
        
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

async def process_video_complete(video_id: str, file_path: str):
    """Process both face extraction and speech transcription"""
    try:
        logger.info(f"Starting background processing for video {video_id}")
        
        # Update status to processing
        await update_video_in_db(video_id, {
            "status": "processing",
            "face_extraction.status": "processing",
            "speech_transcription.status": "processing"
        })
        
        logger.info(f"Updated status to processing for video {video_id}")
        
        # Process faces first (usually faster)
        logger.info(f"Starting face extraction for video {video_id}")
        face_result = processor.extract_faces(file_path, video_id)
        
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
            await update_video_in_db(video_id, face_data)
            logger.info(f"Face extraction completed for video {video_id}: {face_result['faces_detected']} faces found")
        else:
            face_data = {
                "face_extraction": {
                    "status": "failed",
                    "error": face_result["error"],
                    "failed_at": datetime.now().isoformat()
                }
            }
            await update_video_in_db(video_id, face_data)
            logger.error(f"Face extraction failed for video {video_id}: {face_result['error']}")
        
        # Process speech transcription
        logger.info(f"Starting speech transcription for video {video_id}")
        speech_result = processor.extract_and_transcribe_speech(file_path, video_id)
        
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
            await update_video_in_db(video_id, speech_data)
            logger.info(f"Speech transcription completed for video {video_id}: {speech_result['total_segments']} segments")
        else:
            speech_data = {
                "speech_transcription": {
                    "status": "failed",
                    "error": speech_result["error"],
                    "failed_at": datetime.now().isoformat()
                }
            }
            await update_video_in_db(video_id, speech_data)
            logger.error(f"Speech transcription failed for video {video_id}: {speech_result['error']}")
        
        # Update overall status
        video_data = await get_video_from_db(video_id)
        if video_data:
            face_status = video_data["face_extraction"]["status"]
            speech_status = video_data["speech_transcription"]["status"]
            
            if face_status == "completed" and speech_status == "completed":
                final_update = {
                    "status": "completed",
                    "completed_at": datetime.now().isoformat()
                }
                await update_video_in_db(video_id, final_update)
                logger.info(f"All processing completed successfully for video {video_id}")
            elif face_status == "failed" and speech_status == "failed":
                final_update = {
                    "status": "failed",
                    "failed_at": datetime.now().isoformat()
                }
                await update_video_in_db(video_id, final_update)
                logger.error(f"All processing failed for video {video_id}")
            else:
                final_update = {
                    "status": "partial_success",
                    "partial_completed_at": datetime.now().isoformat()
                }
                await update_video_in_db(video_id, final_update)
                logger.warning(f"Partial processing completed for video {video_id}")
        
    except Exception as e:
        logger.error(f"Unexpected error in background processing for video {video_id}: {e}")
        error_update = {
            "status": "failed",
            "error": str(e),
            "failed_at": datetime.now().isoformat()
        }
        await update_video_in_db(video_id, error_update)

@app.get("/status/{video_id}")
async def get_video_status(video_id: str):
    """Get processing status for both face extraction and speech transcription"""
    video_data = await get_video_from_db(video_id)
    
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

@app.get("/transcription/{video_id}")
async def get_transcription(video_id: str):
    """Get speech transcription with timestamps"""
    if video_id not in video_database:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video_database[video_id]
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
        "audio_file_path": speech_data["audio_file_path"]
    }

@app.get("/frames/{video_id}")
async def get_frames_info(video_id: str):
    """Get face extraction information"""
    if video_id not in video_database:
        raise HTTPException(status_code=404, detail="Video not found")
    
    video_data = video_database[video_id]
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

@app.get("/videos")
async def list_videos():
    """List all processed videos"""
    try:
        videos = await get_all_videos_from_db()
        
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
