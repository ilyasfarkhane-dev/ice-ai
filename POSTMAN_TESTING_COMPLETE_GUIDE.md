# 🎬 Complete Postman Testing Guide for Video API with Speech Transcription

## Prerequisites
1. **API Running**: Make sure your API is running on `http://localhost:8000`
2. **MongoDB**: Ensure MongoDB is running locally
3. **Dependencies**: Install the speech processing dependencies
4. **Postman**: Have Postman installed and ready

## Quick Setup Checklist

### 1. Start Your API
```bash
cd /home/farkhane/mini-rag
source venv/bin/activate
python src/main.py
```

### 2. Import Postman Collection
- Open Postman
- Click "Import" → "Upload Files"
- Select: `/home/farkhane/mini-rag/src/assets/video-with-speech-api.postman_collection.json`
- Set Environment Variable: `base_url = http://localhost:8000`

---

## 🧪 Step-by-Step Testing Workflow

### **Step 1: Health Check**
**Purpose**: Verify API is running

**Request**: `GET {{base_url}}/`
```
Method: GET
URL: http://localhost:8000/
```

**Expected Response**:
```json
{
  "message": "Video Processing API with Speech Transcription",
  "status": "running",
  "timestamp": "2025-08-02T..."
}
```

---

### **Step 2: Upload Video with Speech**
**Purpose**: Upload a video that will be processed for both faces and speech

**Request**: `POST {{base_url}}/video/upload`
```
Method: POST
URL: http://localhost:8000/video/upload
Body: form-data
Key: file
Value: [Select a video file with speech - MP4, AVI, MOV]
```

**Expected Response**:
```json
{
  "message": "Video uploaded and processing started",
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "filename": "your_video.mp4",
  "processing_started": true
}
```

**⚠️ IMPORTANT**: Copy the `video_id` from the response and set it as a Postman variable!

---

### **Step 3: Monitor Processing Status**
**Purpose**: Track both video and speech processing progress

**Request**: `GET {{base_url}}/video/status/{{video_id}}`
```
Method: GET
URL: http://localhost:8000/video/status/65f1b2c3d4e5f6789abcdef0
```

**Expected Response (Processing)**:
```json
{
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "filename": "your_video.mp4",
  "status": "processing",
  "transcription_status": "processing",
  "transcription_segments_count": 0,
  "pitch_analysis_points": 0,
  "emotion_classifications": 0
}
```

**Expected Response (Completed)**:
```json
{
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "filename": "your_video.mp4",
  "status": "completed",
  "transcription_status": "completed",
  "transcription_segments_count": 12,
  "pitch_analysis_points": 340,
  "emotion_classifications": 8,
  "processing_stats": {
    "total_frames": 150,
    "faces_detected": 25
  }
}
```

**🔄 Keep checking this endpoint every 10-15 seconds until both statuses show "completed"**

---

### **Step 4: Get Speech Transcription** ⭐ **NEW FEATURE**
**Purpose**: Get timestamped dialogue like your Google Colab example

**Request**: `GET {{base_url}}/video/transcription/{{video_id}}`
```
Method: GET
URL: http://localhost:8000/video/transcription/65f1b2c3d4e5f6789abcdef0
```

**Expected Response**:
```json
{
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "transcription_status": "completed",
  "transcription_segments": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "text": "Can I come in, ma'am?",
      "confidence": 0.95
    },
    {
      "start_time": 8.12,
      "end_time": 10.45,
      "text": "Yes, please come in.",
      "confidence": 0.92
    },
    {
      "start_time": 12.34,
      "end_time": 15.67,
      "text": "Thank you for seeing me.",
      "confidence": 0.88
    }
  ],
  "formatted_transcription": [
    "[5.72s - 7.78s]: Can I come in, ma'am?",
    "[8.12s - 10.45s]: Yes, please come in.",
    "[12.34s - 15.67s]: Thank you for seeing me."
  ],
  "transcription_error": null
}
```

**🎯 This is the main feature - timestamped dialogue exactly like your Google Colab!**

---

### **Step 5: Get Pitch Analysis & Emotions** ⭐ **NEW FEATURE**
**Purpose**: Get voice pitch analysis and emotion classification

**Request**: `GET {{base_url}}/video/pitch-analysis/{{video_id}}`
```
Method: GET
URL: http://localhost:8000/video/pitch-analysis/65f1b2c3d4e5f6789abcdef0
```

**Expected Response**:
```json
{
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "pitch_analysis": [
    {
      "time": 5.72,
      "pitch_hz": 180.5,
      "pitch_normalized": 0.65
    },
    {
      "time": 6.0,
      "pitch_hz": 195.2,
      "pitch_normalized": 0.72
    },
    {
      "time": 6.5,
      "pitch_hz": 175.8,
      "pitch_normalized": 0.61
    }
  ],
  "emotion_classification": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "emotion": "polite_inquiry",
      "confidence": 0.85
    },
    {
      "start_time": 8.12,
      "end_time": 10.45,
      "emotion": "welcoming",
      "confidence": 0.78
    },
    {
      "start_time": 12.34,
      "end_time": 15.67,
      "emotion": "grateful",
      "confidence": 0.82
    }
  ],
  "transcription_status": "completed"
}
```

---

### **Step 6: Get Video Frames (Existing Feature)**
**Purpose**: Get extracted frames with face detection data

**Request**: `GET {{base_url}}/video/frames/{{video_id}}?limit=5`
```
Method: GET
URL: http://localhost:8000/video/frames/65f1b2c3d4e5f6789abcdef0?limit=5
```

**Expected Response**:
```json
{
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "total_frames": 150,
  "frames": [
    {
      "frame_number": 30,
      "timestamp": 1.0,
      "faces_detected": 2,
      "face_coordinates": [
        {"x": 100, "y": 50, "width": 80, "height": 80},
        {"x": 200, "y": 75, "width": 75, "height": 75}
      ]
    }
  ]
}
```

---

### **Step 7: Test Speech-Only Processing** ⭐ **NEW FEATURE**
**Purpose**: Re-transcribe an existing video without reprocessing faces

**Request**: `POST {{base_url}}/video/transcribe-only/{{video_id}}`
```
Method: POST
URL: http://localhost:8000/video/transcribe-only/65f1b2c3d4e5f6789abcdef0
```

**Expected Response**:
```json
{
  "message": "Speech transcription started",
  "video_id": "65f1b2c3d4e5f6789abcdef0",
  "status": "processing"
}
```

**Then monitor with Step 3 again to see transcription progress**

---

### **Step 8: List All Videos**
**Purpose**: See all processed videos with their status

**Request**: `GET {{base_url}}/video/list?limit=10`
```
Method: GET
URL: http://localhost:8000/video/list?limit=10
```

**Expected Response**:
```json
{
  "total": 3,
  "videos": [
    {
      "video_id": "65f1b2c3d4e5f6789abcdef0",
      "filename": "your_video.mp4",
      "status": "completed",
      "transcription_status": "completed",
      "created_at": "2025-08-02T10:30:00Z",
      "transcription_segments_count": 12
    }
  ]
}
```

---

### **Step 9: Download Frames (Optional)**
**Purpose**: Download all extracted frames as a ZIP file

**Request**: `GET {{base_url}}/video/download-frames/{{video_id}}?faces_only=false`
```
Method: GET
URL: http://localhost:8000/video/download-frames/65f1b2c3d4e5f6789abcdef0?faces_only=false
```

**Expected Response**: ZIP file download containing all frame images

---

## 🎯 **Key Features to Test**

### **Speech Transcription Features**:
1. **Timestamped Dialogue**: Like `[5.72s - 7.78s]: Can I come in, ma'am?`
2. **Confidence Scores**: Each transcription segment has a confidence level
3. **Pitch Analysis**: Voice frequency analysis over time
4. **Emotion Classification**: Emotional state detection from speech patterns
5. **Background Processing**: All processing happens asynchronously

### **Face Detection Features**:
1. **Frame Extraction**: Extract frames at configurable intervals
2. **Face Detection**: Detect and locate faces in each frame
3. **Face Cropping**: Extract individual face images
4. **Batch Download**: Download all frames/faces as ZIP

---

## 🐛 **Troubleshooting Common Issues**

### **1. "Video not found" Error**
- Check if you're using the correct `video_id` from the upload response
- Make sure to copy/paste the ID exactly

### **2. Transcription Status Stuck on "processing"**
- Check terminal logs for Whisper model download (first run only)
- Ensure video has audio track
- Verify ffmpeg is installed: `ffmpeg -version`

### **3. "Audio extraction failed"**
- Try a different video format (MP4 recommended)
- Check if video file has audio
- Ensure MoviePy is installed correctly

### **4. Empty transcription results**
- Video might have no speech/dialogue
- Try with a video that has clear speech
- Check audio quality/volume

### **5. API Connection Refused**
- Ensure API is running: `python src/main.py`
- Check MongoDB is running: `sudo systemctl status mongod`
- Verify port 8000 is available

---

## 📱 **Postman Environment Variables**

Set these variables in Postman for easier testing:

```
base_url: http://localhost:8000
video_id: [Update this after each upload]
```

To set variables in Postman:
1. Click the "Environment" tab (eye icon)
2. Click "Add" to create new environment
3. Add the variables above
4. Select the environment before testing

---

## 🎉 **Expected Final Result**

After successful testing, you should have:

1. ✅ **Video uploaded and processed**
2. ✅ **Faces detected and extracted** 
3. ✅ **Speech transcribed with timestamps** like `[5.72s - 7.78s]: Can I come in, ma'am?`
4. ✅ **Pitch analysis completed**
5. ✅ **Emotions classified**
6. ✅ **All data stored in MongoDB**
7. ✅ **Downloadable frame images**

This gives you a complete video analysis system with both visual (faces) and audio (speech) processing! 🚀
