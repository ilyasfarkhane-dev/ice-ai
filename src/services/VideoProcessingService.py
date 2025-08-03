from typing import Dict
import os
import logging
import uuid

logger = logging.getLogger(__name__)

class VideoProcessingService:
    """Service for video face extraction and speech transcription"""
    
    def __init__(self, base_dir: str = "/home/farkhane/mini-rag/src/assets"):
        self.base_dir = base_dir
        self.frames_dir = f"{base_dir}/frames"
        self.audio_dir = f"{base_dir}/audio"
        self.logger = logging.getLogger(__name__)
        self._whisper_model = None  # Lazy loading
        
        # Create directories
        for dir_path in [self.frames_dir, self.audio_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
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
            
            video_frames_dir = os.path.join(self.frames_dir, video_id)
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
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
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
