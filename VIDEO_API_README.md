# Video Face Extraction API

A FastAPI-based service for uploading videos and extracting faces from video frames using MongoDB for data storage.

## 🚀 Quick Start

### 1. Setup MongoDB and Dependencies
```bash
# Run the automated setup
./setup_mongodb.sh

# Or manually:
cd docker && docker-compose up -d mongodb
pip install -r src/requirements.txt
python init_mongodb.py
```

### 2. Start the API Server
```bash
# Development
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

### 3. Import Postman Collection
Import `src/assets/video-face-extraction-api.postman_collection.json` into Postman for easy API testing.

## 📡 API Endpoints

### Upload Video
```http
POST /api/videos/upload
Content-Type: multipart/form-data

Form data:
- file: [video file]
```

**Response:**
```json
{
  "message": "Video uploaded successfully",
  "video_id": "60f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "my_video.mp4",
  "status": "processing_started"
}
```

### Get Video Status
```http
GET /api/videos/{video_id}/status
```

**Response:**
```json
{
  "video_id": "60f7b3b4b3b4b3b4b3b4b3b4",
  "filename": "my_video.mp4",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "processing_stats": {
    "total_frames": 150,
    "frames_with_faces": 89,
    "frames_without_faces": 61,
    "success_rate": 59.33
  }
}
```

### List Videos
```http
GET /api/videos?skip=0&limit=10
```

### Get Video Frames
```http
GET /api/videos/{video_id}/frames?skip=0&limit=20&faces_only=false
```

### Download Frames as ZIP
```http
GET /api/videos/{video_id}/download-frames?faces_only=false
```

### Reprocess Video
```http
POST /api/videos/{video_id}/reprocess?frame_interval=15
```

### Delete Video
```http
DELETE /api/videos/{video_id}
```

## 📊 Processing Status

| Status | Description |
|--------|-------------|
| `uploaded` | Video uploaded, waiting for processing |
| `processing` | Currently extracting frames and detecting faces |
| `completed` | Processing finished successfully |
| `failed` | Processing failed due to an error |
| `deleted` | Video and data have been deleted |

## 📁 File Structure

After uploading and processing a video, files are organized as:

```
src/assets/
├── videos/                           # Uploaded video files
│   └── {uuid}.mp4
└── video_{video_id}/                 # Per-video processing results
    ├── frames/                       # Extracted frames
    │   ├── frame_0000.jpg
    │   ├── frame_0001.jpg
    │   └── ...
    └── faces/                        # Cropped face images
        ├── frame_0000_face.jpg
        ├── frame_0001_face.jpg
        └── ...
```

## 🗄️ Database Schema

### Videos Collection
```javascript
{
  "_id": ObjectId("..."),
  "filename": "my_video.mp4",
  "file_path": "/path/to/video.mp4",
  "file_size": 15728640,
  "content_type": "video/mp4",
  "status": "completed",
  "frame_interval": 30,
  "frames_extracted": 150,
  "faces_found": 89,
  "processing_stats": {...},
  "created_at": ISODate("..."),
  "updated_at": ISODate("..."),
  "processing_started_at": ISODate("..."),
  "processing_completed_at": ISODate("...")
}
```

### Frames Collection
```javascript
{
  "_id": ObjectId("..."),
  "video_id": "60f7b3b4b3b4b3b4b3b4b3b4",
  "frame_number": 0,
  "frame_path": "/path/to/frame_0000.jpg",
  "face_path": "/path/to/frame_0000_face.jpg",
  "face_found": true,
  "created_at": ISODate("..."),
  "processed_at": ISODate("...")
}
```

## 🧪 Testing with Postman

1. **Import Collection**: Import the provided Postman collection
2. **Set Variables**: 
   - `base_url`: `http://localhost:8000`
   - `video_id`: Will be set automatically after upload

3. **Upload Workflow**:
   ```
   1. Upload Video → Get video_id
   2. Check Status → Monitor processing
   3. Get Frames → View extracted frames
   4. Download ZIP → Get all images
   ```

## 🔧 Configuration

### Environment Variables (.env.mongodb)
```bash
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_USERNAME=admin
MONGO_PASSWORD=adminpassword
MONGO_DATABASE=video_faces
MONGO_URI=mongodb://admin:adminpassword@mongodb:27017/video_faces?authSource=admin
```

### Processing Parameters
- **Frame Interval**: Extract every Nth frame (default: 30)
- **Face Detection**: Uses OpenCV Haar Cascade
- **Supported Formats**: MP4, AVI, MOV, WMV, etc.

## 🚨 Error Handling

### Common Issues

1. **File Too Large**
   ```json
   {"detail": "File too large. Maximum size is 100MB"}
   ```

2. **Invalid File Type**
   ```json
   {"detail": "File must be a video"}
   ```

3. **Processing Failed**
   ```json
   {"detail": "No frames could be extracted"}
   ```

4. **Video Not Found**
   ```json
   {"detail": "Video not found"}
   ```

## 📈 Monitoring

### Database Statistics
```bash
# View stats
python mongo_manager.py stats

# List recent videos
python mongo_manager.py list 10

# Clear all data
python mongo_manager.py clear
```

### MongoDB Logs
```bash
# View MongoDB logs
docker-compose -f docker/docker-compose.yml logs mongodb

# Monitor real-time
docker-compose -f docker/docker-compose.yml logs -f mongodb
```

## 🔒 Security Considerations

1. **File Size Limits**: Implement max file size (default: 100MB)
2. **File Type Validation**: Only allow video files
3. **Rate Limiting**: Add rate limiting for uploads
4. **Authentication**: Add user authentication if needed
5. **Storage Cleanup**: Regular cleanup of old files

## 🚀 Production Deployment

### Docker Compose
The video service is already integrated with your existing Docker setup:

```bash
cd docker
docker-compose up -d
```

### Environment Setup
1. Copy `.env.mongodb` to production
2. Update MongoDB credentials
3. Configure file storage paths
4. Set up backup strategy

## 📝 API Documentation

When the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔄 Workflow Example

```python
# 1. Upload video
response = requests.post(
    "http://localhost:8000/api/videos/upload",
    files={"file": open("video.mp4", "rb")}
)
video_id = response.json()["video_id"]

# 2. Monitor processing
while True:
    status = requests.get(f"http://localhost:8000/api/videos/{video_id}/status")
    if status.json()["status"] == "completed":
        break
    time.sleep(5)

# 3. Get results
frames = requests.get(f"http://localhost:8000/api/videos/{video_id}/frames?faces_only=true")
```

This setup provides a complete, production-ready video face extraction service that can be easily tested and integrated into your existing mini-rag application!
