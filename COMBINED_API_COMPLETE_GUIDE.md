# Complete Video Processing API - Face Extraction + Speech Transcription

## Overview
This API combines both face extraction and speech transcription into a single, unified service. When you upload a video via Postman, it will:

1. **Extract faces** from video frames and save cropped face images
2. **Extract audio** from the video and transcribe speech with precise timestamps
3. **Process both simultaneously** in the background for efficiency

## API Endpoints

### 1. Health Check
- **URL**: `GET http://localhost:8000/`
- **Purpose**: Verify API is running and see available features
- **Response**:
```json
{
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
```

### 2. Upload Video for Complete Processing
- **URL**: `POST http://localhost:8000/upload`
- **Body**: Form-data with file field containing your video
- **Supported formats**: MP4, AVI, MOV, MKV, etc.
- **Response**:
```json
{
  "message": "Video uploaded successfully - Face extraction and speech transcription started",
  "video_id": "uuid-generated-id",
  "filename": "your-video.mp4",
  "status": "processing",
  "processing": {
    "face_extraction": "starting",
    "speech_transcription": "starting"
  }
}
```

### 3. Check Processing Status
- **URL**: `GET http://localhost:8000/status/{video_id}`
- **Purpose**: Monitor progress of both face extraction and speech transcription
- **Response**:
```json
{
  "video_id": "uuid-generated-id",
  "filename": "your-video.mp4",
  "status": "completed",  // "processing", "completed", "partial_success", "failed"
  "upload_time": "2024-08-02T23:33:00.000000",
  "face_extraction": {
    "status": "completed",
    "total_frames": 7500,
    "processed_frames": 250,
    "faces_detected": 89,
    "frames_dir": "/path/to/frames/directory"
  },
  "speech_transcription": {
    "status": "completed",
    "audio_file_path": "/path/to/extracted/audio.wav",
    "transcription_segments": [...],
    "formatted_transcription": [...],
    "total_segments": 80,
    "total_duration": 291.5
  }
}
```

### 4. Get Speech Transcription Results
- **URL**: `GET http://localhost:8000/transcription/{video_id}`
- **Purpose**: Get detailed speech transcription with timestamps
- **Response**:
```json
{
  "video_id": "uuid-generated-id",
  "transcription_segments": [
    {
      "start_time": 0.0,
      "end_time": 8.0,
      "text": "Can I come in, ma'am?",
      "confidence": -0.45
    },
    {
      "start_time": 8.5,
      "end_time": 12.0,
      "text": "Yes, please come in.",
      "confidence": -0.32
    }
  ],
  "formatted_transcription": [
    "[0.00s - 8.00s]: Can I come in, ma'am?",
    "[8.50s - 12.00s]: Yes, please come in."
  ],
  "total_segments": 80,
  "total_duration": 291.5,
  "audio_file_path": "/path/to/audio.wav"
}
```

### 5. Get Face Extraction Results
- **URL**: `GET http://localhost:8000/frames/{video_id}`
- **Purpose**: Get face extraction statistics and file locations
- **Response**:
```json
{
  "video_id": "uuid-generated-id",
  "total_frames": 7500,
  "processed_frames": 250,
  "faces_detected": 89,
  "frames_directory": "/path/to/frames/directory"
}
```

### 6. List All Processed Videos
- **URL**: `GET http://localhost:8000/videos`
- **Purpose**: Get summary of all processed videos
- **Response**:
```json
{
  "total_videos": 3,
  "videos": [
    {
      "video_id": "uuid-1",
      "filename": "interview1.mp4",
      "status": "completed",
      "upload_time": "2024-08-02T23:33:00.000000"
    },
    {
      "video_id": "uuid-2",
      "filename": "meeting.avi",
      "status": "processing",
      "upload_time": "2024-08-02T23:35:00.000000"
    }
  ]
}
```

## Step-by-Step Testing in Postman

### Step 1: Import Collection
1. Open Postman
2. Click "Import" button
3. Select the `COMBINED_VIDEO_API_POSTMAN.json` file
4. Collection will be imported with all endpoints ready

### Step 2: Test API Health
1. Select "1. API Health Check" request
2. Click "Send"
3. Verify you get a successful response showing the API is running

### Step 3: Upload Your Video
1. Select "2. Upload Video for Complete Processing" request
2. In the Body tab, click on the "file" field
3. Click "Select Files" and choose your video file
4. Click "Send"
5. **Copy the `video_id` from the response** - you'll need this for other requests

### Step 4: Set Video ID Variable
1. In the collection variables or environment, set the `video_id` variable
2. Use the ID you copied from the upload response

### Step 5: Monitor Processing
1. Select "3. Check Processing Status" request
2. Click "Send" repeatedly to monitor progress
3. Wait until both `face_extraction` and `speech_transcription` show `"completed"`

### Step 6: Get Results
1. Use "4. Get Speech Transcription Results" to see timestamped dialogue
2. Use "5. Get Face Extraction Results" to see face detection statistics
3. Use "6. List All Processed Videos" to see all your processed files

## Expected Output Format

### Speech Transcription Format
The API provides speech transcription in the exact format you requested:
```
[0.00s - 8.00s]: Can I come in, ma'am?
[8.50s - 12.00s]: Yes, please come in.
[13.00s - 18.50s]: Thank you for coming today.
```

### Face Extraction Results
- Saves individual face crops as separate image files
- Provides statistics on frames processed and faces detected
- Creates a organized directory structure for easy access

## File Organization
```
/home/farkhane/mini-rag/src/assets/
├── videos/          # Uploaded video files
├── frames/          # Extracted frames and face crops
│   └── video_id/    # Organized by video ID
└── audio/           # Extracted audio files
```

## Processing Performance
- **Face Extraction**: Processes every 30th frame for efficiency
- **Speech Transcription**: Uses Whisper base model for accuracy
- **Background Processing**: Both operations run simultaneously
- **Memory Management**: Proper cleanup to prevent memory leaks

## Troubleshooting

### If Upload Fails
- Check file format (MP4, AVI, MOV supported)
- Ensure file size is reasonable (< 500MB recommended)
- Verify API is running on localhost:8000

### If Processing Stalls
- Check the status endpoint for error messages
- Look at server logs for detailed error information
- Ensure sufficient disk space for extracted files

### If Transcription is Empty
- Verify the video has audible speech
- Check that audio track exists in the video file
- Try with a different video format

## Success Confirmation
When everything works correctly, you should see:
1. ✅ Video uploaded successfully
2. ✅ Processing status shows both tasks completing
3. ✅ Transcription returns timestamped dialogue
4. ✅ Face extraction shows detected faces count
5. ✅ Files are saved in organized directories

This API now provides exactly what you requested: **combined face extraction + speech transcription via Postman upload** with results in your preferred timestamp format!
