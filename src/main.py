from fastapi import FastAPI
from routes import video
from routes.combined_video import video_router
from helpers.config import get_settings

app = FastAPI(
    title="Mini-RAG Video Processing API",
    description="API for video processing including face extraction and speech transcription",
    version="1.0.0"
)

# Simple startup for video processing
async def startup_span():
    settings = get_settings()
    print(f"Starting Mini-RAG Video Processing API...")
    print(f"MongoDB URL: {settings.MONGODB_URL}")
    print(f"MongoDB Database: {settings.MONGODB_DB_NAME}")
    print(f"Available endpoints:")
    print(f"  - /api/videos/* (Face extraction only)")
    print(f"  - /video/* (Combined face extraction + speech transcription)")

# Simple shutdown for video processing
async def shutdown_span():
    print("Shutting down Mini-RAG Video Processing API...")

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

# Include video routers
app.include_router(video.router)  # Existing face extraction functionality
app.include_router(video_router)  # New combined video processing with MVC architecture
