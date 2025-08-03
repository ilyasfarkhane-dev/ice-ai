#!/bin/bash

# Alternative MongoDB Setup using Docker run command

echo "🚀 Setting up MongoDB using Docker run (alternative method)..."

# Check if Docker is available
if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Stop existing MongoDB container if running
echo "1. Stopping any existing MongoDB container..."
docker stop mongodb 2>/dev/null || true
docker rm mongodb 2>/dev/null || true

# Create Docker network if it doesn't exist
echo "2. Creating Docker network..."
docker network create backend 2>/dev/null || echo "   Network 'backend' already exists"

# Create volumes
echo "3. Creating Docker volumes..."
docker volume create mongodb_data 2>/dev/null || echo "   Volume 'mongodb_data' already exists"
docker volume create mongodb_config 2>/dev/null || echo "   Volume 'mongodb_config' already exists"

# Start MongoDB container
echo "4. Starting MongoDB container..."
docker run -d \
  --name mongodb \
  --network backend \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  -v mongodb_config:/data/configdb \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=adminpassword \
  -e MONGO_INITDB_DATABASE=video_faces \
  --restart always \
  mongo:7.0

# Wait for MongoDB to be ready
echo "5. Waiting for MongoDB to be ready..."
timeout=60
elapsed=0

while ! docker exec mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        echo "❌ MongoDB failed to start within $timeout seconds"
        echo "🔍 Check logs: docker logs mongodb"
        exit 1
    fi
    echo "   Waiting for MongoDB... ($elapsed/$timeout seconds)"
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "6. MongoDB is ready! 🎉"

# Initialize MongoDB
echo "7. Initializing MongoDB collections and indexes..."
cd /home/farkhane/mini-rag
python init_mongodb.py

# Install dependencies
echo "8. Installing Python dependencies..."
pip install -r src/requirements.txt

echo ""
echo "✅ MongoDB setup completed successfully!"
echo ""
echo "📋 Setup Summary:"
echo "   - MongoDB: Running on port 27017"
echo "   - Container: mongodb"
echo "   - Database: video_faces"
echo "   - Username: admin"
echo "   - Password: adminpassword"
echo ""
echo "🔍 MongoDB Management:"
echo "   - View logs: docker logs mongodb"
echo "   - Connect: docker exec -it mongodb mongosh -u admin -p adminpassword"
echo "   - Stop: docker stop mongodb"
echo "   - Start: docker start mongodb"
echo "   - Remove: docker stop mongodb && docker rm mongodb"
echo ""
echo "🎬 Next steps:"
echo "   1. Start API: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo "   2. Test with Postman using the provided collection"
