#!/bin/bash

# Quick Test Script for Video Upload API
# This script demonstrates how to upload a video using curl (similar to Postman)

echo "🚀 Testing Video Upload API..."
echo "================================"

# Check if API is running
echo "1. Checking if API is running..."
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/)
if [ "$response" -eq 200 ]; then
    echo "✅ API is running on localhost:8000"
else
    echo "❌ API is not running. Please start it first:"
    echo "   cd /home/farkhane/mini-rag"
    echo "   source venv/bin/activate"
    echo "   python3 complete_video_api.py"
    exit 1
fi

# Check if user provided a video file
if [ -z "$1" ]; then
    echo ""
    echo "📹 To test video upload, provide a video file:"
    echo "   ./test_video_upload.sh /path/to/your/video.mp4"
    echo ""
    echo "🔍 Available endpoints:"
    curl -s http://localhost:8000/ | python3 -c "
import json, sys
data = json.load(sys.stdin)
print('   📋 Health Check:', 'GET /')
for name, endpoint in data['endpoints'].items():
    print(f'   📋 {name.title()}:', endpoint)
"
    exit 0
fi

VIDEO_FILE="$1"

# Check if file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "❌ Video file not found: $VIDEO_FILE"
    exit 1
fi

echo ""
echo "2. Uploading video: $(basename "$VIDEO_FILE")"
echo "   Size: $(du -h "$VIDEO_FILE" | cut -f1)"

# Upload the video
echo "   Uploading..."
upload_response=$(curl -s -X POST \
    -F "file=@$VIDEO_FILE" \
    http://localhost:8000/upload)

# Parse the response
video_id=$(echo "$upload_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('video_id', 'ERROR'))
except:
    print('ERROR')
")

if [ "$video_id" = "ERROR" ]; then
    echo "❌ Upload failed:"
    echo "$upload_response"
    exit 1
fi

echo "✅ Upload successful!"
echo "   Video ID: $video_id"
echo ""

# Monitor processing status
echo "3. Monitoring processing status..."
for i in {1..20}; do
    echo "   Checking status (attempt $i/20)..."
    
    status_response=$(curl -s "http://localhost:8000/status/$video_id")
    status=$(echo "$status_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    print(data.get('status', 'unknown'))
except:
    print('error')
")
    
    if [ "$status" = "completed" ]; then
        echo "✅ Processing completed!"
        break
    elif [ "$status" = "failed" ]; then
        echo "❌ Processing failed:"
        echo "$status_response"
        exit 1
    else
        echo "   Status: $status"
        sleep 5
    fi
done

# Get results
echo ""
echo "4. Fetching results..."

echo "   📝 Speech Transcription:"
transcription_response=$(curl -s "http://localhost:8000/transcription/$video_id")
echo "$transcription_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'formatted_transcription' in data:
        for line in data['formatted_transcription'][:5]:  # Show first 5 lines
            print(f'      {line}')
        if len(data['formatted_transcription']) > 5:
            print(f'      ... and {len(data[\"formatted_transcription\"]) - 5} more lines')
    else:
        print('      No transcription available yet')
except Exception as e:
    print(f'      Error: {e}')
"

echo ""
echo "   👤 Face Extraction:"
frames_response=$(curl -s "http://localhost:8000/frames/$video_id")
echo "$frames_response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'faces_detected' in data:
        print(f'      Faces detected: {data[\"faces_detected\"]}')
        print(f'      Frames processed: {data[\"processed_frames\"]}')
        print(f'      Total frames: {data[\"total_frames\"]}')
    else:
        print('      No face detection results available yet')
except Exception as e:
    print(f'      Error: {e}')
"

echo ""
echo "🎉 Test completed!"
echo "   Use these URLs in Postman:"
echo "   📋 Status: GET http://localhost:8000/status/$video_id"
echo "   📋 Transcription: GET http://localhost:8000/transcription/$video_id"
echo "   📋 Frames: GET http://localhost:8000/frames/$video_id"
