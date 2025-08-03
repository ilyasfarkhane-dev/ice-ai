import cv2
import os
import asyncio
from PIL import Image
from tqdm import tqdm
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, Any, Optional
from datetime import datetime
from dotenv import load_dotenv
from models.VideoModel import VideoModel, VideoProcessingStatus

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../docker/env/.env.mongodb'))

class VideoFaceExtractorService:
    def __init__(self):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        self.db_name = os.getenv("MONGO_DATABASE", "video_faces")
        self.assets_dir = os.path.join(os.path.dirname(__file__), "../assets")
        
        # Initialize face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    async def get_mongo_client(self):
        """Get async MongoDB client"""
        return AsyncIOMotorClient(self.mongo_uri)

    async def get_frames_collection(self):
        """Get frames collection"""
        client = await self.get_mongo_client()
        db = client[self.db_name]
        return db.frames

    def extract_face(self, src_path: str, dst_path: str) -> bool:
        """Extract face from image"""
        try:
            img = cv2.imread(src_path)
            if img is None:
                return False

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

            if len(faces) == 0:
                return False

            # Take first face only
            x, y, w, h = faces[0]

            # Add margin
            margin = 20
            x = max(x - margin, 0)
            y = max(y - margin, 0)
            w = min(w + 2*margin, img.shape[1] - x)
            h = min(h + 2*margin, img.shape[0] - y)

            face_rgb = cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
            Image.fromarray(face_rgb).save(dst_path)
            return True

        except Exception as e:
            print(f"Error extracting face: {e}")
            return False

    async def extract_frames(self, video_id: str, video_path: str, frame_interval: int = 30) -> int:
        """Extract frames from video"""
        try:
            # Create directories for this video
            frames_dir = os.path.join(self.assets_dir, f"video_{video_id}", "frames")
            faces_dir = os.path.join(self.assets_dir, f"video_{video_id}", "faces")
            os.makedirs(frames_dir, exist_ok=True)
            os.makedirs(faces_dir, exist_ok=True)

            cap = cv2.VideoCapture(video_path)
            frame_count = 0
            saved_count = 0
            frames_collection = await self.get_frames_collection()

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    filename = os.path.join(frames_dir, f"frame_{saved_count:04d}.jpg")
                    cv2.imwrite(filename, frame)

                    # Save frame metadata to MongoDB
                    await frames_collection.insert_one({
                        "video_id": video_id,
                        "frame_number": frame_count,
                        "frame_path": filename,
                        "face_path": None,
                        "face_found": False,
                        "created_at": datetime.utcnow()
                    })
                    saved_count += 1

                frame_count += 1

            cap.release()
            return saved_count

        except Exception as e:
            print(f"Error extracting frames: {e}")
            return 0

    async def process_faces(self, video_id: str) -> Dict[str, int]:
        """Process faces for all frames of a video"""
        try:
            frames_collection = await self.get_frames_collection()
            
            # Get all frames for this video
            cursor = frames_collection.find({"video_id": video_id})
            frames = await cursor.to_list(length=None)
            
            faces_dir = os.path.join(self.assets_dir, f"video_{video_id}", "faces")
            
            total_processed = 0
            faces_found = 0
            
            for frame_doc in tqdm(frames, desc="Processing faces"):
                src_file = frame_doc["frame_path"]
                if not os.path.exists(src_file):
                    continue
                    
                frame_name = os.path.basename(src_file)
                dst_file = os.path.join(faces_dir, os.path.splitext(frame_name)[0] + "_face.jpg")
                
                found = self.extract_face(src_file, dst_file)
                
                # Update frame document
                await frames_collection.update_one(
                    {"_id": frame_doc["_id"]},
                    {
                        "$set": {
                            "face_path": dst_file if found else None,
                            "face_found": found,
                            "processed_at": datetime.utcnow()
                        }
                    }
                )
                
                total_processed += 1
                if found:
                    faces_found += 1

            return {
                "total_processed": total_processed,
                "faces_found": faces_found,
                "faces_not_found": total_processed - faces_found
            }

        except Exception as e:
            print(f"Error processing faces: {e}")
            return {"total_processed": 0, "faces_found": 0, "faces_not_found": 0}

    async def process_video_async(self, video_id: str, video_path: str, frame_interval: int = 30):
        """Process video asynchronously"""
        try:
            # Update status to processing
            await VideoModel.update(video_id, {
                "status": VideoProcessingStatus.PROCESSING.value,
                "processing_started_at": datetime.utcnow()
            })

            # Extract frames
            frames_extracted = await self.extract_frames(video_id, video_path, frame_interval)
            
            if frames_extracted == 0:
                await VideoModel.update(video_id, {
                    "status": VideoProcessingStatus.FAILED.value,
                    "error_message": "No frames could be extracted"
                })
                return

            # Process faces
            face_stats = await self.process_faces(video_id)

            # Update video status to completed
            await VideoModel.update(video_id, {
                "status": VideoProcessingStatus.COMPLETED.value,
                "processing_completed_at": datetime.utcnow(),
                "frames_extracted": frames_extracted,
                "faces_found": face_stats["faces_found"],
                "processing_stats": face_stats
            })

            print(f"✅ Video {video_id} processing completed: {frames_extracted} frames, {face_stats['faces_found']} faces found")

        except Exception as e:
            print(f"❌ Error processing video {video_id}: {e}")
            await VideoModel.update(video_id, {
                "status": VideoProcessingStatus.FAILED.value,
                "error_message": str(e),
                "processing_failed_at": datetime.utcnow()
            })

    async def get_video_stats(self, video_id: str) -> Dict[str, Any]:
        """Get statistics for a video"""
        try:
            frames_collection = await self.get_frames_collection()
            
            total_frames = await frames_collection.count_documents({"video_id": video_id})
            frames_with_faces = await frames_collection.count_documents({"video_id": video_id, "face_found": True})
            frames_without_faces = total_frames - frames_with_faces
            
            success_rate = (frames_with_faces / total_frames * 100) if total_frames > 0 else 0
            
            return {
                "total_frames": total_frames,
                "frames_with_faces": frames_with_faces,
                "frames_without_faces": frames_without_faces,
                "success_rate": round(success_rate, 2)
            }

        except Exception as e:
            print(f"Error getting video stats: {e}")
            return {}

    async def cleanup_video_data(self, video_id: str):
        """Clean up all data associated with a video"""
        try:
            # Remove frames from MongoDB
            frames_collection = await self.get_frames_collection()
            await frames_collection.delete_many({"video_id": video_id})
            
            # Remove files from filesystem
            video_dir = os.path.join(self.assets_dir, f"video_{video_id}")
            if os.path.exists(video_dir):
                import shutil
                shutil.rmtree(video_dir)
                
            print(f"✅ Cleaned up data for video {video_id}")

        except Exception as e:
            print(f"Error cleaning up video data: {e}")
