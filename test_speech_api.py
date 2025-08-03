#!/usr/bin/env python3
"""
Test script for Video Processing API with Speech Transcription
This script demonstrates the complete workflow including speech analysis
"""

import requests
import time
import json
import os

# API Configuration
BASE_URL = "http://localhost:8000"
VIDEO_FILE_PATH = "/path/to/your/video.mp4"  # Update this path

def test_video_upload_with_speech():
    """Test complete video processing including speech transcription"""
    
    print("🎬 Video Processing API with Speech Transcription Test")
    print("=" * 50)
    
    # 1. Check API health
    print("\n1. Checking API health...")
    response = requests.get(f"{BASE_URL}/")
    if response.status_code == 200:
        print("✅ API is running")
    else:
        print("❌ API is not accessible")
        return
    
    # 2. Upload video file
    print(f"\n2. Uploading video file...")
    if not os.path.exists(VIDEO_FILE_PATH):
        print(f"❌ Video file not found: {VIDEO_FILE_PATH}")
        print("Please update VIDEO_FILE_PATH in the script")
        return
    
    with open(VIDEO_FILE_PATH, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/video/upload", files=files)
    
    if response.status_code == 200:
        upload_result = response.json()
        video_id = upload_result['video_id']
        print(f"✅ Video uploaded successfully")
        print(f"   Video ID: {video_id}")
    else:
        print(f"❌ Upload failed: {response.text}")
        return
    
    # 3. Monitor processing status
    print(f"\n3. Monitoring processing status...")
    processing_complete = False
    transcription_complete = False
    max_attempts = 60  # 5 minutes max
    
    for attempt in range(max_attempts):
        response = requests.get(f"{BASE_URL}/video/status/{video_id}")
        if response.status_code == 200:
            status = response.json()
            video_status = status.get('status', 'unknown')
            transcription_status = status.get('transcription_status', 'pending')
            
            print(f"   Attempt {attempt + 1}: Video={video_status}, Transcription={transcription_status}")
            
            if video_status == 'completed':
                processing_complete = True
            if transcription_status == 'completed':
                transcription_complete = True
            
            if processing_complete and transcription_complete:
                print("✅ Both video and transcription processing completed!")
                break
            elif video_status == 'failed' or transcription_status == 'failed':
                print("❌ Processing failed")
                print(f"   Error: {status.get('transcription_error', 'Unknown error')}")
                break
        
        time.sleep(5)  # Wait 5 seconds between checks
    
    if not (processing_complete and transcription_complete):
        print("⏱️ Processing timed out or incomplete")
        return
    
    # 4. Get processing results
    print(f"\n4. Getting processing results...")
    
    # Get video frames
    response = requests.get(f"{BASE_URL}/video/frames/{video_id}?limit=5")
    if response.status_code == 200:
        frames = response.json()
        print(f"✅ Found {len(frames.get('frames', []))} frames with faces")
    
    # Get transcription
    response = requests.get(f"{BASE_URL}/video/transcription/{video_id}")
    if response.status_code == 200:
        transcription = response.json()
        segments = transcription.get('transcription_segments', [])
        formatted = transcription.get('formatted_transcription', [])
        
        print(f"✅ Found {len(segments)} transcription segments")
        print("\n📝 Speech Transcription:")
        for line in formatted[:5]:  # Show first 5 lines
            print(f"   {line}")
        if len(formatted) > 5:
            print(f"   ... and {len(formatted) - 5} more lines")
    
    # Get pitch analysis
    response = requests.get(f"{BASE_URL}/video/pitch-analysis/{video_id}")
    if response.status_code == 200:
        pitch_data = response.json()
        pitch_points = pitch_data.get('pitch_analysis', [])
        emotions = pitch_data.get('emotion_classification', [])
        
        print(f"✅ Found {len(pitch_points)} pitch analysis points")
        print(f"✅ Found {len(emotions)} emotion classifications")
        
        if emotions:
            print("\n😊 Emotion Analysis:")
            for emotion in emotions[:3]:  # Show first 3 emotions
                start = emotion.get('start_time', 0)
                end = emotion.get('end_time', 0)
                emo = emotion.get('emotion', 'unknown')
                conf = emotion.get('confidence', 0)
                print(f"   [{start:.2f}s - {end:.2f}s]: {emo} (confidence: {conf:.2f})")
    
    print(f"\n🎉 Test completed successfully!")
    print(f"Video ID for future reference: {video_id}")

def test_transcription_only():
    """Test transcription-only processing for existing video"""
    video_id = input("Enter video ID for transcription-only test: ").strip()
    if not video_id:
        print("No video ID provided")
        return
    
    print(f"\n🎙️ Testing transcription-only for video {video_id}")
    
    response = requests.post(f"{BASE_URL}/video/transcribe-only/{video_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Transcription started: {result.get('message')}")
        
        # Monitor transcription status
        for attempt in range(30):  # 2.5 minutes max
            response = requests.get(f"{BASE_URL}/video/status/{video_id}")
            if response.status_code == 200:
                status = response.json()
                transcription_status = status.get('transcription_status', 'pending')
                print(f"   Attempt {attempt + 1}: {transcription_status}")
                
                if transcription_status == 'completed':
                    print("✅ Transcription completed!")
                    break
                elif transcription_status == 'failed':
                    print("❌ Transcription failed")
                    break
            
            time.sleep(5)
    else:
        print(f"❌ Failed to start transcription: {response.text}")

if __name__ == "__main__":
    print("Choose test option:")
    print("1. Full video upload with speech transcription")
    print("2. Transcription-only for existing video")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_video_upload_with_speech()
    elif choice == "2":
        test_transcription_only()
    else:
        print("Invalid choice")
