# Video Processing API with Speech Transcription

## Overview
This API processes videos to extract faces and transcribe speech with timestamps, pitch analysis, and emotion classification. Perfect for content analysis and video understanding applications.

## Features

### Video Processing
- Face detection and extraction from video frames
- Frame-by-frame analysis with configurable intervals
- Batch download of extracted frames and faces

### Speech Transcription
- **Timestamped Speech-to-Text**: Extract dialogue with precise timestamps
- **Pitch Analysis**: Analyze voice pitch patterns and frequencies  
- **Emotion Classification**: Classify emotional states from speech patterns
- **Formatted Output**: Display transcription like `[5.72s - 7.78s]: Can I come in, ma'am?`

## API Endpoints

### Video Management
- `POST /video/upload` - Upload video for processing (includes both face extraction and speech transcription)
- `GET /video/status/{video_id}` - Get processing status (includes transcription status)
- `GET /video/list` - List all processed videos
- `DELETE /video/delete/{video_id}` - Delete video and all associated data

### Face Extraction
- `GET /video/frames/{video_id}` - Get extracted frames with face data
- `GET /video/frame/{video_id}/{frame_number}` - Get specific frame
- `GET /video/download-frames/{video_id}` - Download frames as ZIP
- `POST /video/reprocess/{video_id}` - Reprocess with different settings

### Speech Transcription ⭐ NEW
- `GET /video/transcription/{video_id}` - Get speech transcription with timestamps
- `GET /video/pitch-analysis/{video_id}` - Get pitch analysis and emotion classification  
- `POST /video/transcribe-only/{video_id}` - Transcribe existing video without reprocessing faces

## Example Usage

### 1. Upload Video
```bash
curl -X POST "http://localhost:8000/video/upload" \
  -F "file=@your_video.mp4"
```

Response:
```json
{
  "message": "Video uploaded and processing started",
  "video_id": "65a1b2c3d4e5f6789abcdef0",
  "filename": "your_video.mp4"
}
```

### 2. Check Status
```bash
curl "http://localhost:8000/video/status/65a1b2c3d4e5f6789abcdef0"
```

Response:
```json
{
  "video_id": "65a1b2c3d4e5f6789abcdef0",
  "filename": "your_video.mp4",
  "status": "completed",
  "transcription_status": "completed",
  "transcription_segments_count": 15,
  "pitch_analysis_points": 450,
  "emotion_classifications": 8
}
```

### 3. Get Transcription
```bash
curl "http://localhost:8000/video/transcription/65a1b2c3d4e5f6789abcdef0"
```

Response:
```json
{
  "video_id": "65a1b2c3d4e5f6789abcdef0",
  "transcription_status": "completed",
  "transcription_segments": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "text": "Can I come in, ma'am?",
      "confidence": 0.95
    },
    {
      "start_time": 8.12,
      "end_time": 10.45,
      "text": "Yes, please come in.",
      "confidence": 0.92
    }
  ],
  "formatted_transcription": [
    "[5.72s - 7.78s]: Can I come in, ma'am?",
    "[8.12s - 10.45s]: Yes, please come in."
  ]
}
```

### 4. Get Pitch & Emotion Analysis
```bash
curl "http://localhost:8000/video/pitch-analysis/65a1b2c3d4e5f6789abcdef0"
```

Response:
```json
{
  "video_id": "65a1b2c3d4e5f6789abcdef0",
  "pitch_analysis": [
    {
      "time": 5.72,
      "pitch_hz": 180.5,
      "pitch_normalized": 0.65
    }
  ],
  "emotion_classification": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "emotion": "polite_inquiry",
      "confidence": 0.85
    }
  ]
}
```

## Installation & Setup

### 1. Install Dependencies
```bash
# Activate virtual environment
source venv/bin/activate

# Install speech processing libraries
pip install moviepy==1.0.3 openai-whisper==20231117 praat-parselmouth==0.4.3 librosa==0.10.1 soundfile==0.12.1
```

### 2. Start the API
```bash
# Start MongoDB (if not running)
sudo systemctl start mongod

# Start the API
python src/main.py
```

### 3. Test the API
```bash
# Run the test script
python test_speech_api.py
```

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **MongoDB**: Database for storing video metadata and transcription results
- **OpenCV**: Video processing and face detection

### Speech Processing Dependencies ⭐ NEW
- **OpenAI Whisper**: State-of-the-art speech recognition
- **MoviePy**: Audio extraction from video files
- **Praat-Parselmouth**: Pitch analysis and voice feature extraction
- **librosa**: Audio signal processing
- **soundfile**: Audio file I/O

## Architecture

```
Video Upload → Face Extraction (parallel) → MongoDB
             ↘ Audio Extraction → Speech Transcription → Pitch Analysis → Emotion Classification
```

### Processing Pipeline
1. **Video Upload**: Save video file and create database record
2. **Parallel Processing**:
   - **Face Extraction**: Extract frames and detect faces using OpenCV
   - **Audio Extraction**: Extract audio track using MoviePy
3. **Speech Analysis**:
   - **Transcription**: Convert speech to text with timestamps using Whisper
   - **Pitch Analysis**: Analyze voice pitch patterns using Parselmouth
   - **Emotion Classification**: Classify emotions from transcription and pitch data
4. **Storage**: Save all results to MongoDB with structured schema

## Database Schema

### Video Document
```javascript
{
  "_id": ObjectId,
  "filename": "video.mp4",
  "file_path": "/path/to/video.mp4",
  "status": "completed",
  "created_at": ISODate,
  
  // Face extraction data
  "total_frames": 300,
  "processed_frames": 300,
  "extracted_faces": 45,
  
  // Speech transcription data ⭐ NEW
  "audio_file_path": "/path/to/audio.wav",
  "transcription_status": "completed",
  "transcription_segments": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "text": "Can I come in, ma'am?",
      "confidence": 0.95
    }
  ],
  "pitch_analysis": [
    {
      "time": 5.72,
      "pitch_hz": 180.5,
      "pitch_normalized": 0.65
    }
  ],
  "emotion_classification": [
    {
      "start_time": 5.72,
      "end_time": 7.78,
      "emotion": "polite_inquiry",
      "confidence": 0.85
    }
  ]
}
```

## Postman Collection

Import the provided Postman collection for easy API testing:
- File: `src/assets/video-with-speech-api.postman_collection.json`
- Contains all 13 endpoints with examples
- Includes sample responses for speech transcription

## Error Handling

The API handles various error scenarios gracefully:

- **Video Processing Errors**: Continues with speech transcription even if face detection fails
- **Audio Extraction Errors**: Marks transcription as failed but preserves video processing results
- **Transcription Errors**: Saves error details while maintaining video metadata
- **Background Processing**: Errors are logged and stored in the database for debugging

## Performance Considerations

### Speech Processing Performance
- **Whisper Model**: Uses base model for balance of speed and accuracy
- **Parallel Processing**: Face extraction and speech transcription run simultaneously
- **Memory Management**: Audio files are processed in chunks to manage memory usage
- **Background Tasks**: All processing happens asynchronously to maintain API responsiveness

### Recommended Hardware
- **CPU**: Multi-core processor for parallel processing
- **RAM**: 8GB+ recommended for Whisper model
- **Storage**: SSD recommended for video file I/O
- **GPU**: Optional, can accelerate Whisper transcription

## Troubleshooting

### Common Issues

1. **Whisper Installation**:
   ```bash
   # If ffmpeg is missing
   sudo apt install ffmpeg  # Ubuntu/Debian
   brew install ffmpeg      # macOS
   ```

2. **Praat Installation**:
   ```bash
   # If praat-parselmouth fails to install
   sudo apt install build-essential  # Ubuntu/Debian
   ```

3. **Audio Extraction Fails**:
   - Ensure video file has audio track
   - Check video codec compatibility
   - Verify ffmpeg installation

4. **MongoDB Connection**:
   ```bash
   # Check MongoDB status
   sudo systemctl status mongod
   
   # Start MongoDB
   sudo systemctl start mongod
   ```

## Contributing

When adding new speech processing features:
1. Update the `SpeechTranscriptionService` class
2. Add corresponding controller methods
3. Create new API endpoints in routes
4. Update the database schema
5. Add tests to the test script
6. Update this documentation

## License

This project follows the same license as the original mini-rag project.
