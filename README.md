# ICE-AI: Intelligent Video Processing API

A comprehensive video processing API built with FastAPI that combines face extraction and speech transcription with confidence scoring. Features proper MVC architecture, MongoDB storage, and asynchronous processing.

## 🚀 Features

- **Face Extraction**: Extract faces from video frames using OpenCV
- **Speech Transcription**: Convert speech to text using OpenAI Whisper with confidence scoring
- **Confidence Analysis**: 
  - Overall video confidence percentage (e.g., 94.1%)
  - Individual segment confidence scores
  - Quality ratings (Excellent, Good, Fair, Poor, Very Poor)
- **Persistent Storage**: MongoDB with automatic fallback to in-memory storage
- **Background Processing**: Asynchronous video processing for better performance
- **MVC Architecture**: Clean separation of concerns with Models, Views, and Controllers
- **RESTful API**: Well-documented endpoints with FastAPI automatic documentation

## 🏗️ Architecture

```
src/
├── main.py                 # FastAPI application entry point
├── requirements.txt        # Python dependencies
├── controllers/           # Business logic coordination
│   ├── CombinedVideoController.py
│   ├── VideoController.py
│   └── ...
├── models/               # Data access layer
│   ├── CombinedVideoModel.py
│   ├── VideoModel.py
│   └── ...
├── services/             # Business logic
│   ├── VideoProcessingService.py
│   └── ...
├── routes/               # API endpoints
│   ├── combined_video.py
│   ├── video.py
│   └── ...
├── helpers/              # Utilities and configuration
│   └── config.py
└── assets/               # Static files and uploads
    └── videos/
```

## 📋 Prerequisites

- Python 3.8+
- MongoDB (optional - will fallback to in-memory storage)
- FFmpeg (for video processing)
- Git

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-pip python3-venv ffmpeg mongodb
```

**macOS:**
```bash
brew install python ffmpeg mongodb-community
```

**Windows:**
- Install Python from [python.org](https://python.org)
- Install FFmpeg from [ffmpeg.org](https://ffmpeg.org)
- Install MongoDB from [mongodb.com](https://mongodb.com)

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone git@github.com:ilyasfarkhane-dev/ice-ai.git
cd ice-ai
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r src/requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# MongoDB Configuration (optional)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=video_faces

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001

# Upload Configuration
UPLOAD_DIR=/path/to/your/uploads
MAX_FILE_SIZE=100MB
```

### 5. Start MongoDB (Optional)

If you want to use MongoDB for persistent storage:

```bash
# Ubuntu/Debian
sudo systemctl start mongod

# macOS
brew services start mongodb-community

# Or run directly
mongod --dbpath /path/to/your/db
```

### 6. Run the Application

```bash
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

The API will be available at: `http://localhost:8001`

## 📚 API Documentation

Once the application is running, visit:

- **Interactive Docs**: `http://localhost:8001/docs`
- **ReDoc**: `http://localhost:8001/redoc`

### Key Endpoints

#### Combined Video Processing (New MVC Architecture)

- `POST /video/upload` - Upload video for processing
- `GET /video/status/{video_id}` - Check processing status
- `GET /video/transcription/{video_id}` - Get speech transcription with confidence
- `GET /video/frames/{video_id}` - Get face extraction results
- `GET /video/list` - List all processed videos
- `GET /video/health` - Health check
- `GET /video/info` - Service information

#### Legacy Face Extraction

- `POST /api/videos/upload` - Upload video for face extraction only
- `GET /api/videos/{video_id}/status` - Get face extraction status
- `GET /api/videos/` - List videos with pagination

## 🎯 Usage Examples

### Upload and Process Video

```bash
# Upload a video file
curl -X POST "http://localhost:8001/video/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_video.mp4"

# Response:
{
  "message": "Video uploaded successfully! Processing started in background.",
  "video_id": "uuid-here",
  "filename": "your_video.mp4",
  "status": "uploaded",
  "processing": {
    "face_extraction": "queued",
    "speech_transcription": "queued"
  }
}
```

### Check Processing Status

```bash
curl -X GET "http://localhost:8001/video/status/{video_id}"

# Response:
{
  "video_id": "uuid-here",
  "filename": "your_video.mp4",
  "status": "completed",
  "face_extraction": {
    "status": "completed",
    "faces_detected": 15,
    "total_frames": 120
  },
  "speech_transcription": {
    "status": "completed",
    "total_segments": 25,
    "overall_confidence_percentage": 94.1,
    "overall_confidence_quality": "Excellent"
  }
}
```

### Get Transcription Results

```bash
curl -X GET "http://localhost:8001/video/transcription/{video_id}"

# Response:
{
  "video_id": "uuid-here",
  "transcription_segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "Hello, how are you today?",
      "confidence": -0.15,
      "confidence_percentage": 87.4,
      "confidence_quality": "Good"
    }
  ],
  "overall_confidence": -0.149,
  "overall_confidence_percentage": 94.1,
  "overall_confidence_quality": "Excellent",
  "total_segments": 25
}
```

## 🧪 Testing

### Health Check

```bash
curl -X GET "http://localhost:8001/video/health"
# Response: {"status":"healthy","service":"combined_video_processing"}
```

### Service Information

```bash
curl -X GET "http://localhost:8001/video/info"
```

## 🔧 Configuration

### File Upload Limits

Default maximum file size is 100MB. Configure in your environment:

```env
MAX_FILE_SIZE=200MB
```

### Storage Configuration

- **MongoDB**: Persistent storage with automatic reconnection
- **Fallback**: In-memory storage if MongoDB is unavailable
- **Upload Directory**: Configurable via `UPLOAD_DIR` environment variable

### Confidence Scoring

The system converts Whisper's log probabilities to user-friendly percentages:

- **Raw Score**: -0.149 (Whisper's log probability)
- **Percentage**: 94.1% (converted for user understanding)
- **Quality**: "Excellent" (human-readable rating)

Quality ratings:
- 95-100%: Excellent
- 85-94%: Good  
- 70-84%: Fair
- 50-69%: Poor
- <50%: Very Poor

## 🚀 Deployment

### Docker Deployment

```bash
# Build image
docker build -t ice-ai .

# Run container
docker run -p 8001:8001 \
  -e MONGODB_URL=mongodb://host.docker.internal:27017 \
  -v $(pwd)/uploads:/app/uploads \
  ice-ai
```

### Production Deployment

For production, consider:

1. **Reverse Proxy**: Use Nginx or similar
2. **Process Manager**: Use Gunicorn with multiple workers
3. **Environment Variables**: Set production configurations
4. **Monitoring**: Add logging and monitoring solutions
5. **Security**: Configure CORS, authentication, and HTTPS

```bash
# Production run with Gunicorn
pip install gunicorn
cd src
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues

**MongoDB Connection Failed**
- Ensure MongoDB is running: `sudo systemctl status mongod`
- Check MongoDB URL in `.env` file
- The application will automatically fallback to in-memory storage

**FFmpeg Not Found**
- Install FFmpeg: `sudo apt install ffmpeg` (Ubuntu) or `brew install ffmpeg` (macOS)
- Ensure FFmpeg is in your PATH

**Import Errors**
- Activate virtual environment: `source venv/bin/activate`
- Install dependencies: `pip install -r src/requirements.txt`

**Permission Errors**
- Check upload directory permissions
- Ensure the application has write access to the upload folder

### Performance Optimization

For large video files:
- Increase `MAX_FILE_SIZE` in environment variables
- Configure adequate disk space for uploads
- Consider implementing video compression
- Use background task queues for heavy processing

## 📞 Support

For support, please open an issue on GitHub or contact the development team.

---

**Made with ❤️ by the ICE-AI Team**
| 11 | Mongo Indexing                        | [Video](https://www.youtube.com/watch?v=iO8FAmUVcjE) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-008) |
| 12 | Data Pipeline Enhancements                        | [Video](https://www.youtube.com/watch?v=4x1DuezZBDU) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-008) |
| 13 | Checkpoint-1                        | [Video](https://www.youtube.com/watch?v=7xIsZkCisPk) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-008) |
| 14 | LLM Factory                        | [Video](https://www.youtube.com/watch?v=5TKRIFtIQAY) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-008) |
| 15 | Vector DB Factory                        | [Video](https://www.youtube.com/watch?v=JtS9UkvF_10) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-009) |
| 16 | Semantic Search                       | [Video](https://www.youtube.com/watch?v=V3swQKokJW8) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-010) |
| 17 | Augmented Answers                       | [Video](https://www.youtube.com/watch?v=1Wx8BoM5pLU) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-011) |
| 18 | Checkpoint-1 + Fix Issues                       | [Video](https://youtu.be/6zG4Idxldvg) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-012) |
| 19 | Ollama Local LLM Server                       | [Video](https://youtu.be/-epZ1hAAtrs) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-012) |
| 20 | From Mongo to Postgres + SQLAlchemy & Alembic                       | [Video](https://www.youtube.com/watch?v=BVOq7Ek2Up0) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-013) |
| 21 | The way to PgVector                       | [Video](https://www.youtube.com/watch?v=g99yq5zlYAE) | [branch](https://github.com/bakrianoo/mini-rag/tree/tut-014) |


## Requirements

- Python 3.10

#### Install Dependencies

```bash
sudo apt update
sudo apt install libpq-dev gcc python3-dev
```

#### Install Python using MiniConda

1) Download and install MiniConda from [here](https://docs.anaconda.com/free/miniconda/#quick-command-line-install)
2) Create a new environment using the following command:
```bash
$ conda create -n mini-rag python=3.10
```
3) Activate the environment:
```bash
$ conda activate mini-rag
```

### (Optional) Setup you command line interface for better readability

```bash
export PS1="\[\033[01;32m\]\u@\h:\w\n\[\033[00m\]\$ "
```

### (Optional) Run Ollama Local LLM Server using Colab + Ngrok

- Check the [notebook](https://colab.research.google.com/drive/1KNi3-9KtP-k-93T3wRcmRe37mRmGhL9p?usp=sharing) + [Video](https://youtu.be/-epZ1hAAtrs)

## Installation

### Install the required packages

```bash
$ pip install -r requirements.txt
```

### Setup the environment variables

```bash
$ cp .env.example .env
```

### Run Alembic Migration

```bash
$ alembic upgrade head
```

Set your environment variables in the `.env` file. Like `OPENAI_API_KEY` value.

## Run Docker Compose Services

```bash
$ cd docker
$ cp .env.example .env
```

- update `.env` with your credentials



```bash
$ cd docker
$ sudo docker compose up -d
```

## Run the FastAPI server

```bash
$ uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## POSTMAN Collection

Download the POSTMAN collection from [/assets/mini-rag-app.postman_collection.json](/assets/mini-rag-app.postman_collection.json)
