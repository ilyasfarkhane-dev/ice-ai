#!/bin/bash

# Quick Test Script for Video Face Extraction API
# This script demonstrates the API workflow using curl commands

echo "🎬 Video Face Extraction API - Quick Test"
echo "========================================"

BASE_URL="http://localhost:8000"
TEST_VIDEO="test_video.mp4"  # Replace with your test video path

# Check if API is running
echo "1. Checking API status..."
if curl -s "$BASE_URL/docs" > /dev/null; then
    echo "✅ API is running at $BASE_URL"
else
    echo "❌ API is not running. Start it with: uvicorn src.main:app --reload"
    exit 1
fi

# Test 1: Upload video
echo ""
echo "2. Uploading video..."
if [ ! -f "$TEST_VIDEO" ]; then
    echo "⚠️  Test video not found: $TEST_VIDEO"
    echo "   Please update TEST_VIDEO path in this script"
    exit 1
fi

UPLOAD_RESPONSE=$(curl -s -X POST \
  "$BASE_URL/api/videos/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$TEST_VIDEO")

echo "Upload response: $UPLOAD_RESPONSE"

# Extract video_id from response
VIDEO_ID=$(echo $UPLOAD_RESPONSE | grep -o '"video_id":"[^"]*"' | cut -d'"' -f4)

if [ -z "$VIDEO_ID" ]; then
    echo "❌ Failed to get video_id from upload response"
    exit 1
fi

echo "✅ Video uploaded successfully. Video ID: $VIDEO_ID"

# Test 2: Check status
echo ""
echo "3. Checking processing status..."
STATUS_RESPONSE=$(curl -s "$BASE_URL/api/videos/$VIDEO_ID/status")
echo "Status response: $STATUS_RESPONSE"

# Test 3: List videos
echo ""
echo "4. Listing all videos..."
LIST_RESPONSE=$(curl -s "$BASE_URL/api/videos?limit=5")
echo "List response: $LIST_RESPONSE"

# Test 4: Wait for processing and get frames
echo ""
echo "5. Waiting for processing to complete..."
for i in {1..30}; do
    STATUS=$(curl -s "$BASE_URL/api/videos/$VIDEO_ID/status" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "   Status check $i: $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Processing completed!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Processing failed!"
        exit 1
    fi
    
    sleep 10
done

# Test 5: Get frames
echo ""
echo "6. Getting extracted frames..."
FRAMES_RESPONSE=$(curl -s "$BASE_URL/api/videos/$VIDEO_ID/frames?limit=5")
echo "Frames response: $FRAMES_RESPONSE"

# Test 6: Get frames with faces only
echo ""
echo "7. Getting frames with faces only..."
FACES_RESPONSE=$(curl -s "$BASE_URL/api/videos/$VIDEO_ID/frames?faces_only=true&limit=5")
echo "Faces response: $FACES_RESPONSE"

echo ""
echo "🎉 Test completed successfully!"
echo ""
echo "📋 Summary:"
echo "   Video ID: $VIDEO_ID"
echo "   You can now test in Postman with this video_id"
echo ""
echo "🔗 Useful URLs:"
echo "   API Docs: $BASE_URL/docs"
echo "   Video Status: $BASE_URL/api/videos/$VIDEO_ID/status"
echo "   Download Frames: $BASE_URL/api/videos/$VIDEO_ID/download-frames"
echo "   Download Faces: $BASE_URL/api/videos/$VIDEO_ID/download-frames?faces_only=true"
