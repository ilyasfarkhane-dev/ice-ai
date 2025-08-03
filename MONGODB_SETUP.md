# MongoDB Setup for Video Face Extraction

This guide will help you set up MongoDB for the video face extraction project.

## Quick Start

### Option 1: Using Docker (Recommended)

1. **Run the setup script:**
   ```bash
   ./setup_mongodb.sh
   ```

2. **Or manually start MongoDB:**
   ```bash
   cd docker
   docker-compose up -d mongodb
   ```

### Option 2: Local MongoDB Installation

#### Ubuntu/Debian:
```bash
# Import the public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Update and install
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### macOS:
```bash
# Using Homebrew
brew tap mongodb/brew
brew install mongodb-community@7.0
brew services start mongodb/brew/mongodb-community
```

## Configuration

### Environment Variables (.env.mongodb)
```bash
MONGO_HOST=mongodb
MONGO_PORT=27017
MONGO_USERNAME=admin
MONGO_PASSWORD=adminpassword
MONGO_DATABASE=video_faces
MONGO_URI=mongodb://admin:adminpassword@mongodb:27017/video_faces?authSource=admin
```

### Local Development
For local development, update the `MONGO_URI` in your script to:
```python
MONGO_URI = "mongodb://localhost:27017/video_faces"
```

## Usage

### 1. Install Python Dependencies
```bash
pip install -r src/requirements.txt
```

### 2. Run Video Face Extraction
```bash
# Update VIDEO_PATH in src/assets/video_face_extractor.py first
python src/assets/video_face_extractor.py
```

### 3. Monitor Progress
```bash
# View database statistics
python mongo_manager.py stats

# List recent frames
python mongo_manager.py list 20

# Clear database (if needed)
python mongo_manager.py clear
```

## Database Schema

### Collection: `frames`
```javascript
{
  "_id": ObjectId("..."),
  "frame_number": 0,           // Original frame number from video
  "frame_path": "/path/to/frame_0000.jpg",  // Full frame image path
  "face_path": "/path/to/frame_0000_face.jpg",  // Cropped face image path (null if no face)
  "face_found": true           // Boolean indicating if face was detected
}
```

### Indexes
- `frame_number`: For efficient frame lookups
- `face_found`: For filtering frames with/without faces

## Troubleshooting

### Connection Issues
```bash
# Check if MongoDB is running
docker-compose -f docker/docker-compose.yml ps mongodb

# View MongoDB logs
docker-compose -f docker/docker-compose.yml logs mongodb

# Connect to MongoDB shell
docker-compose -f docker/docker-compose.yml exec mongodb mongosh -u admin -p adminpassword
```

### Performance Tips
1. **Batch Processing**: Process multiple frames before database updates
2. **Indexing**: Ensure indexes are created for frequent queries
3. **Connection Pooling**: Use connection pooling for high-volume processing

## File Structure
```
src/assets/
├── video_face_extractor.py    # Main processing script
├── full_frames/               # Extracted video frames
└── faces_cropped/             # Detected and cropped faces

docker/
├── docker-compose.yml         # MongoDB service definition
└── env/
    └── .env.mongodb          # MongoDB configuration

mongo_manager.py              # Database management utilities
setup_mongodb.sh             # Automated setup script
```

## Next Steps

1. Place your video file in `src/assets/`
2. Update `VIDEO_PATH` in `video_face_extractor.py`
3. Run the extraction script
4. Use `mongo_manager.py` to monitor progress and manage data
