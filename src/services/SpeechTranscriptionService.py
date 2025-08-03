import os
# Lazy import heavy libraries to avoid blocking startup
# import whisper
# import parselmouth
# import numpy as np
# from moviepy.editor import VideoFileClip
from typing import Dict, List, Optional
import asyncio
import logging

logger = logging.getLogger(__name__)

class SpeechTranscriptionService:
    """Service for extracting audio, transcribing speech, and analyzing pitch from videos"""
    
    def __init__(self):
        self.whisper_model = None
        self.audio_dir = "uploads/audio"
        self.transcription_dir = "uploads/transcriptions"
        
        # Create directories if they don't exist
        os.makedirs(self.audio_dir, exist_ok=True)
        os.makedirs(self.transcription_dir, exist_ok=True)
    
    def load_whisper_model(self, model_size: str = "base"):
        """Load Whisper model for transcription"""
        try:
            # Lazy import whisper when actually needed
            import whisper
            
            if self.whisper_model is None:
                logger.info(f"Loading Whisper model: {model_size}")
                self.whisper_model = whisper.load_model(model_size)
                logger.info("Whisper model loaded successfully")
            return self.whisper_model
        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise
    
    def extract_audio(self, video_path: str, video_id: str) -> str:
        """Extract audio from video file"""
        try:
            # Lazy import moviepy when actually needed
            from moviepy.editor import VideoFileClip
            
            audio_filename = f"video_{video_id}_audio.wav"
            audio_path = os.path.join(self.audio_dir, audio_filename)
            
            logger.info(f"Extracting audio from {video_path}")
            clip = VideoFileClip(video_path)
            clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
            clip.close()
            
            logger.info(f"Audio extracted to {audio_path}")
            return audio_path
            
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            raise
    
    def transcribe_with_timestamps(self, audio_path: str, video_id: str) -> Dict:
        """Transcribe audio with timestamps using Whisper"""
        try:
            # Load model if not already loaded
            model = self.load_whisper_model()
            
            logger.info(f"Transcribing audio: {audio_path}")
            result = model.transcribe(audio_path, word_timestamps=True)
            
            # Format transcription with timestamps
            formatted_transcription = []
            transcription_text = ""
            
            for segment in result['segments']:
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()
                
                formatted_line = f"[{start_time:.2f}s - {end_time:.2f}s]: {text}"
                formatted_transcription.append(formatted_line)
                transcription_text += formatted_line + "\n"
            
            # Save transcription to file
            transcription_filename = f"video_{video_id}_transcription.txt"
            transcription_path = os.path.join(self.transcription_dir, transcription_filename)
            
            with open(transcription_path, 'w', encoding='utf-8') as f:
                f.write(transcription_text)
            
            logger.info(f"Transcription completed. {len(formatted_transcription)} segments found")
            
            return {
                "segments": result['segments'],
                "formatted_transcription": formatted_transcription,
                "transcription_text": transcription_text,
                "transcription_path": transcription_path,
                "language": result.get('language', 'unknown'),
                "total_segments": len(formatted_transcription)
            }
            
        except Exception as e:
            logger.error(f"Error during transcription: {e}")
            raise
    
    def analyze_pitch(self, audio_path: str) -> Dict:
        """Analyze pitch and emotion from audio"""
        try:
            # Lazy import parselmouth and numpy when actually needed
            import parselmouth
            import numpy as np
            
            logger.info(f"Analyzing pitch for: {audio_path}")
            
            # Load audio with Parselmouth
            snd = parselmouth.Sound(audio_path)
            pitch = snd.to_pitch()
            pitch_values = pitch.selected_array['frequency']
            
            # Remove zero values (unvoiced segments)
            voiced_pitch = pitch_values[pitch_values > 0]
            
            if len(voiced_pitch) == 0:
                logger.warning("No voiced segments found in audio")
                return {
                    "average_pitch": 0,
                    "min_pitch": 0,
                    "max_pitch": 0,
                    "pitch_std": 0,
                    "emotion": "Unknown - No voice detected",
                    "pitch_analysis": "No voiced segments detected"
                }
            
            # Calculate pitch statistics
            avg_pitch = np.mean(voiced_pitch)
            min_pitch = np.min(voiced_pitch)
            max_pitch = np.max(voiced_pitch)
            pitch_std = np.std(voiced_pitch)
            
            # Classify emotion based on pitch
            emotion = self.classify_emotion(avg_pitch)
            
            logger.info(f"Pitch analysis completed. Average pitch: {avg_pitch:.2f} Hz")
            
            return {
                "average_pitch": round(avg_pitch, 2),
                "min_pitch": round(min_pitch, 2),
                "max_pitch": round(max_pitch, 2),
                "pitch_std": round(pitch_std, 2),
                "emotion": emotion,
                "pitch_analysis": f"Average pitch: {avg_pitch:.2f} Hz - {emotion}"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing pitch: {e}")
            return {
                "average_pitch": 0,
                "min_pitch": 0,
                "max_pitch": 0,
                "pitch_std": 0,
                "emotion": "Error in analysis",
                "pitch_analysis": f"Error: {str(e)}"
            }
    
    def classify_emotion(self, avg_pitch: float) -> str:
        """Classify emotion based on average pitch"""
        if avg_pitch < 140:
            return "Calm / Deep Voice"
        elif avg_pitch < 200:
            return "Neutral / Confident"
        elif avg_pitch < 250:
            return "Animated / Engaged"
        else:
            return "Excited / High-pitched / Nervous"
    
    async def process_video_audio(self, video_path: str, video_id: str) -> Dict:
        """Complete audio processing pipeline"""
        try:
            result = {
                "video_id": video_id,
                "audio_extracted": False,
                "transcription_completed": False,
                "pitch_analysis_completed": False,
                "error": None
            }
            
            # Step 1: Extract audio
            logger.info(f"Starting audio processing for video {video_id}")
            audio_path = self.extract_audio(video_path, video_id)
            result["audio_path"] = audio_path
            result["audio_extracted"] = True
            
            # Step 2: Transcribe with timestamps
            transcription_result = self.transcribe_with_timestamps(audio_path, video_id)
            result.update(transcription_result)
            result["transcription_completed"] = True
            
            # Step 3: Analyze pitch
            pitch_result = self.analyze_pitch(audio_path)
            result.update(pitch_result)
            result["pitch_analysis_completed"] = True
            
            logger.info(f"Audio processing completed for video {video_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error in audio processing pipeline: {e}")
            result["error"] = str(e)
            return result
    
    def get_transcription_summary(self, transcription_result: Dict) -> str:
        """Generate a summary of the transcription"""
        if not transcription_result.get("formatted_transcription"):
            return "No transcription available"
        
        summary = f"""
🎵 Speech Transcription Results:
================================

📝 Total Segments: {transcription_result.get('total_segments', 0)}
🌍 Language: {transcription_result.get('language', 'Unknown')}
📊 Average Pitch: {transcription_result.get('average_pitch', 0)} Hz
🔊 Estimated Emotion: {transcription_result.get('emotion', 'Unknown')}

📋 Transcription:
{chr(10).join(transcription_result.get('formatted_transcription', []))}
"""
        return summary
    
    def cleanup_temp_files(self, video_id: str):
        """Clean up temporary audio files"""
        try:
            audio_file = os.path.join(self.audio_dir, f"video_{video_id}_audio.wav")
            if os.path.exists(audio_file):
                os.remove(audio_file)
                logger.info(f"Cleaned up audio file: {audio_file}")
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")
