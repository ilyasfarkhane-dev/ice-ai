# 📋 Complete Postman API Documentation
## Video Face Extraction API - All Endpoints

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Content-Type**: `application/json` (except file uploads)

---

## 🎬 **1. Upload Video**

### **Endpoint**
```
POST /api/videos/upload
```

### **Description**
Upload a video file for face extraction processing. The API will extract frames, detect faces, and store results in MongoDB.

### **Postman Setup**
1. **Method**: `POST`
2. **URL**: `http://localhost:8000/api/videos/upload`
3. **Headers**:
   ```
   accept: application/json
   ```
4. **Body**: Select `form-data`
   ```
   Key: file
   Type: File
   Value: [Select your video file]
   ```

### **Supported File Types**
- `.mp4`, `.avi`, `.mov`, `.webm`
- Max size: ~50MB (recommended for testing)

### **Response Example**
```json
{
  "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
  "filename": "my_video.mp4",
  "status": "uploaded",
  "message": "Video uploaded successfully. Processing started in background.",
  "file_size": 15728640,
  "upload_time": "2025-08-02T20:30:15Z"
}
```

### **Error Responses**
```json
// Missing file
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "file"],
      "msg": "Field required",
      "input": null
    }
  ]
}

// Invalid file type
{
  "detail": "Unsupported file type. Supported formats: mp4, avi, mov, webm"
}
```

---

## 📊 **2. Get Video Status**

### **Endpoint**
```
GET /api/videos/{video_id}/status
```

### **Description**
Get current processing status and statistics for an uploaded video.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/status`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Path Parameters**
- `video_id` (string, required): ID of the uploaded video

### **Response Example**
```json
{
  "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
  "filename": "my_video.mp4",
  "status": "completed",
  "frames_extracted": 45,
  "faces_found": 23,
  "file_size": 15728640,
  "created_at": "2025-08-02T20:30:15Z",
  "updated_at": "2025-08-02T20:32:45Z",
  "processing_time": "2m 30s",
  "progress": {
    "current_frame": 45,
    "total_frames": 45,
    "percentage": 100
  }
}
```

### **Status Values**
- `uploaded`: Video uploaded, waiting to start processing
- `processing`: Currently extracting frames and detecting faces
- `completed`: Processing finished successfully
- `failed`: Processing failed due to error

---

## 📋 **3. List All Videos**

### **Endpoint**
```
GET /api/videos/
```

### **Description**
Get a paginated list of all uploaded videos with their status and metadata.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/?skip=0&limit=10`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Query Parameters**
- `skip` (integer, optional): Number of videos to skip (default: 0)
- `limit` (integer, optional): Maximum number of videos to return (1-100, default: 10)

### **Response Example**
```json
{
  "videos": [
    {
      "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
      "filename": "video1.mp4",
      "status": "completed",
      "frames_extracted": 45,
      "faces_found": 23,
      "created_at": "2025-08-02T20:30:15Z"
    },
    {
      "video_id": "64f7b3b4c8d9e1f2a3b4c5d7",
      "filename": "video2.avi",
      "status": "processing",
      "frames_extracted": 12,
      "faces_found": 8,
      "created_at": "2025-08-02T20:35:20Z"
    }
  ],
  "total": 2,
  "skip": 0,
  "limit": 10
}
```

---

## 🖼️ **4. Get Video Frames**

### **Endpoint**
```
GET /api/videos/{video_id}/frames
```

### **Description**
Get metadata for extracted frames including paths to frame images and face crops.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/frames?skip=0&limit=20&faces_only=false`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Path Parameters**
- `video_id` (string, required): ID of the video

### **Query Parameters**
- `skip` (integer, optional): Number of frames to skip (default: 0)
- `limit` (integer, optional): Maximum frames to return (1-100, default: 20)
- `faces_only` (boolean, optional): Return only frames with detected faces (default: false)

### **Response Example**
```json
{
  "frames": [
    {
      "frame_id": "64f7b3b4c8d9e1f2a3b4c5d8",
      "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
      "frame_number": 0,
      "frame_path": "/uploads/frames/video_64f7b3b4_frame_0000.jpg",
      "face_path": "/uploads/faces/video_64f7b3b4_frame_0000_face.jpg",
      "face_found": true,
      "timestamp": "00:00:00",
      "created_at": "2025-08-02T20:31:10Z"
    }
  ],
  "total_frames": 45,
  "frames_with_faces": 23,
  "skip": 0,
  "limit": 20
}
```

---

## 👥 **5. Get Frames with Faces Only**

### **Endpoint**
```
GET /api/videos/{video_id}/frames?faces_only=true
```

### **Description**
Get only frames where faces were detected. Same as endpoint #4 but with `faces_only=true`.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/frames?faces_only=true&limit=50`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Query Parameters**
- `faces_only`: `true` (required for this use case)
- `limit`: Number of frames to return (optional)

---

## 📦 **6. Download Extracted Frames (ZIP)**

### **Endpoint**
```
GET /api/videos/{video_id}/download-frames
```

### **Description**
Download all extracted frames as a ZIP file.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/download-frames?faces_only=false`
3. **Headers**:
   ```
   accept: application/zip
   ```

### **Query Parameters**
- `faces_only` (boolean, optional): 
  - `false`: Download all extracted frames
  - `true`: Download only face crops

### **Response**
- **Content-Type**: `application/zip`
- **Filename**: `video_{video_id}_frames.zip`
- **Contents**: All extracted frame images

### **Postman Download Settings**
1. After sending request, click **Save Response** 
2. Choose **Save to file**
3. File will be saved as ZIP

---

## 👤 **7. Download Face Crops Only (ZIP)**

### **Endpoint**
```
GET /api/videos/{video_id}/download-frames?faces_only=true
```

### **Description**
Download only the detected face crops as a ZIP file.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/download-frames?faces_only=true`
3. **Headers**:
   ```
   accept: application/zip
   ```

### **Response**
- **Content-Type**: `application/zip`
- **Filename**: `video_{video_id}_faces.zip`
- **Contents**: Only extracted face images

---

## 🔄 **8. Reprocess Video**

### **Endpoint**
```
POST /api/videos/{video_id}/reprocess
```

### **Description**
Reprocess a video with different settings. Clears existing data and starts fresh processing.

### **Postman Setup**
1. **Method**: `POST`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}/reprocess?frame_interval=30`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Query Parameters**
- `frame_interval` (integer, optional): New frame extraction interval (1-120 frames)

### **Response Example**
```json
{
  "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
  "message": "Video reprocessing started with new settings",
  "status": "processing",
  "new_settings": {
    "frame_interval": 30
  }
}
```

---

## 🗑️ **9. Delete Video**

### **Endpoint**
```
DELETE /api/videos/{video_id}
```

### **Description**
Delete a video and all associated data including files and database records.

### **Postman Setup**
1. **Method**: `DELETE`
2. **URL**: `http://localhost:8000/api/videos/{{video_id}}`
3. **Headers**:
   ```
   accept: application/json
   ```

### **Response Example**
```json
{
  "video_id": "64f7b3b4c8d9e1f2a3b4c5d6",
  "message": "Video and all associated data deleted successfully",
  "deleted_items": {
    "video_file": true,
    "frames": 45,
    "faces": 23,
    "database_records": 46
  }
}
```

---

## 📖 **10. API Documentation**

### **Endpoint**
```
GET /docs
```

### **Description**
Access interactive API documentation powered by FastAPI and Swagger UI.

### **Postman Setup**
1. **Method**: `GET`
2. **URL**: `http://localhost:8000/docs`
3. **Headers**:
   ```
   accept: text/html
   ```

### **Usage**
- Open in browser for interactive testing
- View all endpoints with examples
- Test API directly from the browser

---

## 🔧 **Postman Environment Variables**

Set these variables for easier testing:

```json
{
  "base_url": "http://localhost:8000",
  "video_id": "{{video_id}}"
}
```

### **Auto-Save Video ID Script**
Add this to the **Tests** tab of the upload request:

```javascript
// Auto-save video_id from upload response
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.video_id) {
        pm.environment.set('video_id', response.video_id);
        console.log('Video ID saved: ' + response.video_id);
    }
}
```

---

## 📝 **Testing Workflow**

### **Complete Test Sequence**:
1. **Upload** → Get `video_id`
2. **Status** → Monitor processing progress  
3. **List** → See all videos
4. **Frames** → View extracted frame metadata
5. **Download** → Get ZIP with results
6. **Delete** → Clean up (optional)

### **Quick Test Commands**:
```bash
# 1. Upload
POST /api/videos/upload (with file)

# 2. Check status  
GET /api/videos/{video_id}/status

# 3. Download faces
GET /api/videos/{video_id}/download-frames?faces_only=true
```

---

## 🎯 **Common Response Codes**

- **200 OK**: Request successful
- **307 Temporary Redirect**: Automatic redirect (normal)
- **422 Unprocessable Entity**: Validation error (check request format)
- **404 Not Found**: Video ID not found
- **500 Internal Server Error**: Server processing error

This documentation covers all available endpoints in the Video Face Extraction API! 🚀
