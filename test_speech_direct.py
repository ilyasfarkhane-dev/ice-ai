#!/usr/bin/env python3
"""
Direct Speech Transcription Script
Test speech transcription without the full API
"""

import os
import sys
import logging

# Add current directory to Python path
sys.path.append('/home/farkhane/mini-rag/src')

def test_speech_transcription(video_path: str):
    """Test speech transcription directly"""
    
    print(f"🎬 Testing Speech Transcription for: {video_path}")
    print("=" * 60)
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return
    
    try:
        # Import with error handling
        print("📦 Loading speech processing libraries...")
        
        import whisper
        print("✅ Whisper loaded")
        
        from moviepy.editor import VideoFileClip
        print("✅ MoviePy loaded")
        
        import parselmouth
        print("✅ Parselmouth loaded")
        
        print("\n🎵 Step 1: Extracting audio...")
        
        # Extract audio
        clip = VideoFileClip(video_path)
        audio_path = "/tmp/test_audio.wav"
        clip.audio.write_audiofile(audio_path, verbose=False, logger=None)
        clip.close()
        print(f"✅ Audio extracted to: {audio_path}")
        
        print("\n🎙️ Step 2: Loading Whisper model...")
        model = whisper.load_model("base")
        print("✅ Whisper model loaded")
        
        print("\n📝 Step 3: Transcribing speech...")
        result = model.transcribe(audio_path)
        
        print("\n🎯 TRANSCRIPTION RESULTS:")
        print("-" * 40)
        
        for segment in result['segments']:
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            
            # Format like your Google Colab example
            formatted = f"[{start:.2f}s - {end:.2f}s]: {text}"
            print(formatted)
        
        print(f"\n📊 SUMMARY:")
        print(f"Total segments: {len(result['segments'])}")
        print(f"Total duration: {result['segments'][-1]['end']:.2f}s" if result['segments'] else "0s")
        
        # Clean up
        os.remove(audio_path)
        print(f"\n✅ Test completed successfully!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Run: pip install openai-whisper moviepy praat-parselmouth")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Test with your video
    video_path = "/home/farkhane/mini-rag/src/assets/videos"
    
    print("🔍 Looking for video files...")
    if os.path.exists(video_path):
        videos = [f for f in os.listdir(video_path) if f.endswith(('.mp4', '.avi', '.mov'))]
        if videos:
            test_video = os.path.join(video_path, videos[0])
            print(f"📹 Found video: {videos[0]}")
            test_speech_transcription(test_video)
        else:
            print("❌ No video files found")
            print(f"Upload a video to: {video_path}")
    else:
        print(f"❌ Video directory not found: {video_path}")
        
    print("\n💡 To test with a specific video:")
    print(f"python3 {__file__} /path/to/your/video.mp4")
