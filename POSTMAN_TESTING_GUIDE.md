# Testing Video Face Extraction API with Postman

## 🚀 Step-by-Step Testing Guide

### Prerequisites
1. **Start the services:**
   ```bash
   # Setup MongoDB and dependencies
   ./setup_mongodb.sh
   
   # Start the FastAPI server
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Verify services are running:**
   - API: http://localhost:8000/docs
   - MongoDB: Running in Docker

### 📥 Import Postman Collection

1. **Open Postman**
2. **Click "Import"** in the top left
3. **Choose "Upload Files"**
4. **Select:** `/home/farkhane/mini-rag/src/assets/video-face-extraction-api.postman_collection.json`
5. **Click "Import"**

### 🔧 Configure Environment Variables

After importing, you'll see variables in the collection:
- `base_url`: Already set to `http://localhost:8000`
- `video_id`: Will be set automatically after upload

### 🎬 Testing Workflow

## Test 1: Upload a Video

1. **Select:** `Upload Video` request
2. **Go to Body tab**
3. **Click on "file" field**
4. **Click "Select Files"**
5. **Choose your video file** (MP4, AVI, MOV, etc.)
6. **Click Send**

**Expected Response:**
```json
{
  "message": "Video uploaded successfully",
  "video_id": "64f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "your_video.mp4",
  "status": "processing_started"
}
```

**⚠️ Important:** Copy the `video_id` from the response!

### 📋 Set Video ID Variable

1. **In Postman, click the collection name**
2. **Go to Variables tab**
3. **Paste the video_id** in both "Initial Value" and "Current Value"
4. **Click Save**

## Test 2: Check Processing Status

1. **Select:** `Get Video Status` request
2. **Click Send** (video_id variable will be used automatically)

**Expected Response:**
```json
{
  "video_id": "64f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "your_video.mp4",
  "status": "processing",  // or "completed"
  "created_at": "2024-08-02T10:30:00Z",
  "processing_stats": {
    "total_frames": 0,      // Will increase during processing
    "frames_with_faces": 0,
    "frames_without_faces": 0,
    "success_rate": 0
  }
}
```

**Keep checking this endpoint until status becomes "completed"**

## Test 3: List All Videos

1. **Select:** `List All Videos` request
2. **Click Send**

**Expected Response:**
```json
{
  "videos": [
    {
      "_id": "64f7b3b4b3b4b3b4b3b4b3b4",
      "filename": "your_video.mp4",
      "status": "completed",
      "created_at": "2024-08-02T10:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

## Test 4: Get Video Frames

1. **Select:** `Get Video Frames` request
2. **Click Send**

**Expected Response:**
```json
{
  "frames": [
    {
      "_id": "64f7b3b4b3b4b3b4b3b4b3b5",
      "video_id": "64f7b3b4b3b4b3b4b3b4b3b4",
      "frame_number": 0,
      "frame_path": "/path/to/frame_0000.jpg",
      "face_path": "/path/to/frame_0000_face.jpg",
      "face_found": true,
      "created_at": "2024-08-02T10:31:00Z"
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 20,
  "faces_only": false
}
```

## Test 5: Get Only Frames with Faces

1. **Select:** `Get Frames with Faces Only` request
2. **Click Send**

This will return only frames where faces were detected.

## Test 6: Download Files

### Download All Frames as ZIP
1. **Select:** `Download Frames ZIP` request
2. **Click Send**
3. **Save the ZIP file** when prompted

### Download Only Face Images as ZIP
1. **Select:** `Download Faces ZIP` request
2. **Click Send**
3. **Save the ZIP file** when prompted

## Test 7: Reprocess Video (Optional)

1. **Select:** `Reprocess Video` request
2. **Modify frame_interval** in query params (e.g., change to 15)
3. **Click Send**

This will reprocess the video with a different frame extraction interval.

## Test 8: Delete Video

1. **Select:** `Delete Video` request
2. **Click Send**

**Expected Response:**
```json
{
  "message": "Video deleted successfully",
  "video_id": "64f7b3b4b3b4b3b4b3b4b3b4"
}
```

### 🔍 Monitoring and Debugging

## Check API Documentation
Visit http://localhost:8000/docs for interactive API documentation.

## Monitor Processing
```bash
# Check MongoDB data
python mongo_manager.py stats

# View recent frames
python mongo_manager.py list 10

# Check Docker logs
docker-compose -f docker/docker-compose.yml logs mongodb
```

## Check File System
```bash
# Check uploaded videos
ls -la src/assets/videos/

# Check processed data
ls -la src/assets/video_*/
```

### 🐛 Common Issues and Solutions

## Issue 1: Connection Refused
**Error:** `Connection refused to localhost:8000`
**Solution:**
```bash
# Make sure FastAPI is running
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Issue 2: MongoDB Connection Error
**Error:** `MongoDB connection failed`
**Solution:**
```bash
# Check MongoDB is running
docker-compose -f docker/docker-compose.yml ps mongodb

# Restart if needed
docker-compose -f docker/docker-compose.yml restart mongodb
```

## Issue 3: File Too Large
**Error:** `413 Request Entity Too Large`
**Solution:** Reduce video file size or increase FastAPI file size limits.

## Issue 4: Processing Stuck
**Solution:**
```bash
# Check processing status
python mongo_manager.py stats

# Check API logs
tail -f /path/to/api/logs
```

### 📊 Expected Processing Times

| Video Length | File Size | Frames | Processing Time |
|-------------|-----------|---------|----------------|
| 1 minute    | 10MB      | ~120    | 30-60 seconds  |
| 5 minutes   | 50MB      | ~600    | 2-5 minutes    |
| 10 minutes  | 100MB     | ~1200   | 5-10 minutes   |

### 🎯 Success Indicators

✅ **Upload Success:** 
- Status code: 200
- Response contains video_id
- Status: "processing_started"

✅ **Processing Complete:**
- Status: "completed"
- processing_stats shows frame counts
- Files exist in assets folder

✅ **Frame Extraction Success:**
- Frames array contains frame data
- face_found: true for frames with faces
- Files accessible via file paths

### 🔄 Complete Test Sequence

```
1. Upload Video → Get video_id → Set in Postman variables
2. Check Status → Wait for "completed"
3. List Videos → Verify video appears
4. Get Frames → View extraction results
5. Download ZIP → Get processed files
6. Optional: Reprocess → Different settings
7. Delete Video → Cleanup
```

This comprehensive testing guide will help you verify that your video face extraction API is working correctly with all the dynamic upload functionality!
