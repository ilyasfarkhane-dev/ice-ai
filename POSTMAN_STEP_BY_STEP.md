# 🧪 Postman Testing Guide - Video Face Extraction API

## 📥 Quick Setup (5 minutes)

### Step 1: Import Collection
1. **Open Postman**
2. **Click "Import"** button (top-left)
3. **Drag & drop** or **browse** to select:
   ```
   /home/farkhane/mini-rag/src/assets/video-face-extraction-api.postman_collection.json
   ```
4. **Click "Import"**

### Step 2: Start Services
```bash
# Terminal 1: Start MongoDB and dependencies
./setup_mongodb.sh

# Terminal 2: Start API server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 3: Verify Setup
- ✅ API Docs: http://localhost:8000/docs
- ✅ MongoDB: `docker ps | grep mongodb`

---

## 🎬 Testing Workflow

### 🔄 Test Sequence Overview
```
Upload Video → Check Status → Get Frames → Download ZIP → Delete
     ↓              ↓             ↓            ↓          ↓
   Get video_id   Monitor       View         Get files   Cleanup
                processing    results
```

---

## 📋 Detailed Test Steps

### 1️⃣ **Upload Video**

**Request:** `POST /api/videos/upload`

**Steps:**
1. Select **"Upload Video"** request
2. Go to **Body** tab
3. Click **"Select Files"** next to "file"
4. Choose your video file (MP4, AVI, MOV, etc.)
5. Click **"Send"**

**Expected Response:**
```json
{
  "message": "Video uploaded successfully",
  "video_id": "64f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "my_video.mp4",
  "status": "processing_started"
}
```

**🔥 IMPORTANT:** Copy the `video_id` value!

### 2️⃣ **Set Video ID Variable**

1. Click **collection name** in sidebar
2. Go to **Variables** tab
3. Find **"video_id"** row
4. Paste video_id in **"Current value"** column
5. Click **"Save"**

### 3️⃣ **Check Processing Status**

**Request:** `GET /api/videos/{video_id}/status`

**Steps:**
1. Select **"Get Video Status"** request
2. Click **"Send"**
3. **Repeat every 30 seconds** until status = "completed"

**Status Progression:**
```
uploaded → processing → completed
```

**Completed Response:**
```json
{
  "video_id": "64f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "my_video.mp4",
  "status": "completed",
  "processing_stats": {
    "total_frames": 150,
    "frames_with_faces": 89,
    "frames_without_faces": 61,
    "success_rate": 59.33
  }
}
```

### 4️⃣ **View Extracted Frames**

**Request:** `GET /api/videos/{video_id}/frames`

**Steps:**
1. Select **"Get Video Frames"** request
2. Click **"Send"**
3. Review frame data and file paths

**Response Sample:**
```json
{
  "frames": [
    {
      "frame_number": 0,
      "frame_path": "/app/assets/video_64f7.../frames/frame_0000.jpg",
      "face_path": "/app/assets/video_64f7.../faces/frame_0000_face.jpg",
      "face_found": true
    }
  ],
  "total": 150
}
```

### 5️⃣ **Get Only Faces**

**Request:** `GET /api/videos/{video_id}/frames?faces_only=true`

**Steps:**
1. Select **"Get Frames with Faces Only"** request
2. Click **"Send"**
3. This returns only frames where faces were detected

### 6️⃣ **Download Results**

#### Download All Frames
1. Select **"Download Frames ZIP"** request
2. Click **"Send"**
3. **Save file** when prompted

#### Download Only Faces
1. Select **"Download Faces ZIP"** request
2. Click **"Send"**
3. **Save file** when prompted

### 7️⃣ **List All Videos**

**Request:** `GET /api/videos`

**Steps:**
1. Select **"List All Videos"** request
2. Click **"Send"**
3. View all uploaded videos with pagination

---

## 🔧 Advanced Testing

### **Reprocess Video with Different Settings**

**Request:** `POST /api/videos/{video_id}/reprocess?frame_interval=15`

**Steps:**
1. Select **"Reprocess Video"** request
2. Modify **frame_interval** parameter (e.g., 15, 60)
3. Click **"Send"**
4. Monitor status again

### **Delete Video**

**Request:** `DELETE /api/videos/{video_id}`

**Steps:**
1. Select **"Delete Video"** request
2. Click **"Send"**
3. Confirms deletion of video and all associated data

---

## 🔍 Testing Tips

### **Verify Each Step:**
- ✅ **Upload:** Check for video_id in response
- ✅ **Status:** Wait for "completed" status
- ✅ **Frames:** Verify frame_found: true entries
- ✅ **Files:** Check that ZIP downloads work

### **Monitor Progress:**
```bash
# Check database stats
python mongo_manager.py stats

# Check file system
ls -la src/assets/video_*/
```

### **Test Different Videos:**
- Short video (1-2 minutes): Quick test
- Long video (5+ minutes): Performance test
- No faces video: Edge case test
- Multiple faces video: Detection test

---

## 🐛 Troubleshooting

### **Common Issues:**

| Issue | Solution |
|-------|----------|
| "Connection refused" | Start API: `uvicorn src.main:app --reload` |
| "MongoDB error" | Check: `docker-compose ps mongodb` |
| "File too large" | Use smaller video or increase limits |
| "Processing stuck" | Check: `python mongo_manager.py stats` |
| "No video_id" | Check upload response format |

### **Status Codes:**
- `200` ✅ Success
- `400` ❌ Bad request (check file format)
- `404` ❌ Video not found (check video_id)
- `500` ❌ Server error (check logs)

---

## 📊 Expected Results

### **Good Performance Indicators:**
- Face detection rate: **40-80%** (depends on video content)
- Processing time: **~1 frame per second**
- File sizes: Faces typically 10-20% of original frame size

### **File Structure After Processing:**
```
src/assets/
├── videos/
│   └── {uuid}.mp4                    # Original uploaded video
└── video_{video_id}/
    ├── frames/                       # All extracted frames
    │   ├── frame_0000.jpg
    │   └── frame_0001.jpg
    └── faces/                        # Cropped face images
        ├── frame_0000_face.jpg
        └── frame_0001_face.jpg
```

---

## 🚀 Quick Test Command

For command-line testing:
```bash
# Run automated test
./test_api.sh
```

This provides a complete testing workflow that validates your dynamic video upload and face extraction system!
