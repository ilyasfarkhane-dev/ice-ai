# How to Upload Video in Postman - Step by Step Guide

## Prerequisites
✅ **API is running** on `http://localhost:8000`  
✅ **Postman installed** on your computer  
✅ **Video file ready** (MP4, AVI, MOV, etc.)

## Method 1: Manual Setup in Postman

### Step 1: Create New Request
1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Change method from `GET` to **`POST`**
4. Enter URL: `http://localhost:8000/upload`

### Step 2: Configure Request Body
1. In the request window, click the **"Body"** tab
2. Select **"form-data"** (NOT raw or JSON)
3. In the key field, type: `file`
4. Click the dropdown next to the key field and select **"File"** (not "Text")
5. Click **"Select Files"** button that appears
6. Browse and select your video file

### Step 3: Send Request
1. Click the blue **"Send"** button
2. Wait for response (should be almost immediate)
3. Copy the `video_id` from the response - you'll need this!

### Step 4: Check Processing Status
1. Create another GET request to: `http://localhost:8000/status/YOUR_VIDEO_ID`
2. Replace `YOUR_VIDEO_ID` with the ID from step 3
3. Send this request every 30 seconds to monitor progress

---

## Method 2: Import Ready-Made Collection

### Step 1: Import Collection
1. Download the collection file: `COMBINED_VIDEO_API_POSTMAN.json`
2. In Postman, click **"Import"** (top left)
3. Drag and drop the JSON file or click "Upload Files"
4. Collection will appear in your sidebar

### Step 2: Use Upload Request
1. In the imported collection, find **"2. Upload Video for Complete Processing"**
2. Click on it to open
3. Go to **"Body"** tab
4. Click **"Select Files"** next to the `file` field
5. Choose your video file
6. Click **"Send"**

---

## Visual Guide: Postman Form-Data Setup

```
Request Type: POST
URL: http://localhost:8000/upload

Body Tab → form-data:
┌─────────────────────────────────────┐
│ KEY      │ TYPE │ VALUE            │
├─────────────────────────────────────┤
│ file     │ File │ [Select Files]   │
│          │  ▼   │ your-video.mp4   │
└─────────────────────────────────────┘
```

## Expected Response After Upload

```json
{
  "message": "Video uploaded successfully - Face extraction and speech transcription started",
  "video_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "filename": "your-video.mp4",
  "status": "processing",
  "processing": {
    "face_extraction": "starting",
    "speech_transcription": "starting"
  }
}
```

## Complete Testing Workflow

### 1. Upload Video
```
POST http://localhost:8000/upload
Body: form-data with file field
```

### 2. Monitor Progress
```
GET http://localhost:8000/status/{video_id}
```

### 3. Get Speech Transcription
```
GET http://localhost:8000/transcription/{video_id}
```

### 4. Get Face Extraction Results
```
GET http://localhost:8000/frames/{video_id}
```

## Common Issues and Solutions

### ❌ **"Unsupported Media Type" Error**
**Problem**: You selected "raw" or "JSON" instead of "form-data"  
**Solution**: Go to Body tab → Select "form-data" → Set key as "file" with type "File"

### ❌ **"Field required" Error**
**Problem**: The key name is wrong or file type not selected  
**Solution**: Ensure key is exactly `file` and type is set to "File" (not "Text")

### ❌ **404 Not Found Error**
**Problem**: Wrong URL or API not running  
**Solution**: Check URL is `http://localhost:8000/upload` (no `/api/` prefix)

### ❌ **Connection Refused Error**
**Problem**: API server is not running  
**Solution**: Start the API with: `cd /home/farkhane/mini-rag && source venv/bin/activate && python3 complete_video_api.py`

## Test with Sample Video

If you don't have a video handy, you can:
1. **Record a short video** with your phone (10-30 seconds)
2. **Download a sample video** from the internet
3. **Use any video format**: MP4, AVI, MOV, MKV

## What Happens After Upload

1. **Immediate Response**: You get a `video_id` and confirmation
2. **Background Processing**: 
   - Face detection extracts faces from video frames
   - Audio extraction creates WAV file from video
   - Whisper transcribes speech with timestamps
3. **Results Available**: Check status endpoint until both processes complete
4. **Get Results**: Use transcription and frames endpoints

## Example Complete Test Session

```bash
# 1. Upload video
POST http://localhost:8000/upload
→ Response: {"video_id": "abc123", "status": "processing"}

# 2. Check status (repeat until completed)
GET http://localhost:8000/status/abc123
→ Response: {"status": "completed", "face_extraction": {...}, "speech_transcription": {...}}

# 3. Get speech transcription
GET http://localhost:8000/transcription/abc123
→ Response: {"formatted_transcription": ["[0.00s - 8.00s]: Hello there"]}

# 4. Get face extraction results
GET http://localhost:8000/frames/abc123
→ Response: {"faces_detected": 5, "frames_directory": "/path/to/frames"}
```

---

## Quick Start Checklist

- [ ] API running on localhost:8000
- [ ] Postman open
- [ ] POST request to `http://localhost:8000/upload`
- [ ] Body tab → form-data
- [ ] Key: `file`, Type: File
- [ ] Video file selected
- [ ] Send button clicked
- [ ] video_id copied from response
- [ ] Status checked until completion
- [ ] Results retrieved

**You're now ready to upload videos and get both face extraction + speech transcription results!** 🎉
