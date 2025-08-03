# Simple MongoDB Setup for Video Face Extraction (Local MongoDB)

## Prerequisites
✅ MongoDB is already installed and running on your system

## 🚀 Quick Setup Steps (5 minutes)

### Step 1: Start MongoDB Service
```bash
# Start MongoDB service (if not already running)
sudo systemctl start mongod

# Enable MongoDB to start on boot (optional)
sudo systemctl enable mongod

# Check if MongoDB is running
sudo systemctl status mongod
```

### Step 2: Create Database and Collections
```bash
# Connect to MongoDB
mongosh

# Switch to video_faces database (creates it if doesn't exist)
use video_faces

# Create collections with indexes
db.videos.createIndex({ "status": 1 })
db.videos.createIndex({ "created_at": 1 })
db.videos.createIndex({ "filename": 1 })

db.frames.createIndex({ "video_id": 1 })
db.frames.createIndex({ "frame_number": 1 })
db.frames.createIndex({ "face_found": 1 })
db.frames.createIndex({ "video_id": 1, "frame_number": 1 })
db.frames.createIndex({ "video_id": 1, "face_found": 1 })

# Verify collections created
show collections

# Exit MongoDB shell
exit
```

### Step 3: Update Environment Configuration
Create or update the MongoDB environment file:

```bash
# Create environment file
cat > /home/farkhane/mini-rag/docker/env/.env.mongodb << EOF
MONGO_HOST=localhost
MONGO_PORT=27017
MONGO_USERNAME=
MONGO_PASSWORD=
MONGO_DATABASE=video_faces
MONGO_URI=mongodb://localhost:27017/video_faces
EOF
```

### Step 4: Create Python Virtual Environment and Install Dependencies
```bash
cd /home/farkhane/mini-rag

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r src/requirements.txt
```

**Note:** Always activate the virtual environment before running the API:
```bash
source venv/bin/activate
```

### Step 5: Initialize Database (Python Script)
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run the initialization script
python init_mongodb.py
```

### Step 6: Start the API Server
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Start FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Test Your Setup

### Verify MongoDB Connection
```bash
# Test MongoDB connection
mongosh --eval "db.adminCommand('ping')"

# Check your database
mongosh video_faces --eval "db.stats()"
```

### Test API
```bash
# Check API is running
curl http://localhost:8000/docs

# Test video endpoints
curl http://localhost:8000/api/videos
```

## 📊 Database Structure

### Database: `video_faces`
### Collections:
- **`videos`** - Video metadata and processing status
- **`frames`** - Individual frame data and face detection results

### Sample Data:
```javascript
// Videos collection
{
  "_id": ObjectId("..."),
  "filename": "my_video.mp4",
  "file_path": "/path/to/video.mp4",
  "status": "completed",
  "frames_extracted": 150,
  "faces_found": 89,
  "created_at": ISODate("...")
}

// Frames collection
{
  "_id": ObjectId("..."),
  "video_id": "64f7b3b4...",
  "frame_number": 0,
  "frame_path": "/path/to/frame_0000.jpg",
  "face_path": "/path/to/frame_0000_face.jpg",
  "face_found": true,
  "created_at": ISODate("...")
}
```

## 🔧 Management Commands

### View Database Stats
```bash
# Connect and view stats
mongosh video_faces

# In MongoDB shell:
db.videos.countDocuments()      // Count videos
db.frames.countDocuments()      // Count frames
db.frames.countDocuments({"face_found": true})  // Count frames with faces

# Exit
exit
```

### Clear Database (if needed)
```bash
mongosh video_faces --eval "db.videos.deleteMany({}); db.frames.deleteMany({})"
```

### Backup Database
```bash
# Backup
mongodump --db video_faces --out /path/to/backup

# Restore
mongorestore --db video_faces /path/to/backup/video_faces
```

## 🎬 Ready to Test!

Now you can:
1. **Import Postman collection**: `src/assets/video-face-extraction-api.postman_collection.json`
2. **Upload videos** via POST `/api/videos/upload`
3. **Monitor processing** via GET `/api/videos/{id}/status`
4. **Download results** via GET `/api/videos/{id}/download-frames`

## 🔍 Troubleshooting

### MongoDB not starting?
```bash
sudo systemctl restart mongod
sudo systemctl status mongod
```

### Permission issues?
```bash
sudo chown -R mongodb:mongodb /var/lib/mongodb
sudo chown -R mongodb:mongodb /var/log/mongodb
```

### API connection issues?
- Check MongoDB is running: `sudo systemctl status mongod`
- Verify port 27017 is open: `sudo netstat -tlnp | grep 27017`
- Check environment file: `cat docker/env/.env.mongodb`

That's it! Your local MongoDB setup is ready for video face extraction. 🚀
