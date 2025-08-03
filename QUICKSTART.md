# 🚀 Quick Start Guide

Get ICE-AI running in under 5 minutes!

## Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone git@github.com:ilyasfarkhane-dev/ice-ai.git
cd ice-ai

# Start with Docker Compose
docker-compose up -d

# Check if everything is running
curl http://localhost:8001/video/health
```

**That's it!** Your API is now running at:
- **API**: http://localhost:8001
- **API Docs**: http://localhost:8001/docs
- **MongoDB Express**: http://localhost:8081 (admin/admin123)

## Option 2: Local Development

```bash
# Clone and setup
git clone git@github.com:ilyasfarkhane-dev/ice-ai.git
cd ice-ai

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r src/requirements.txt

# Start the API
cd src
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8001
```

## Quick Test

Upload a video file:

```bash
curl -X POST "http://localhost:8001/video/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_video.mp4"
```

Check the status:

```bash
curl -X GET "http://localhost:8001/video/status/YOUR_VIDEO_ID"
```

## Next Steps

1. Visit http://localhost:8001/docs for full API documentation
2. Check the main README.md for detailed configuration options
3. Upload a test video and explore the confidence scoring features

## Need Help?

- 📖 Check the main [README.md](README.md) for full documentation
- 🐛 Open an issue on GitHub for bugs
- 💡 Join our community for questions and discussions
