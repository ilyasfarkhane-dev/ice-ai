#!/bin/bash

# MongoDB Setup Script for Video Face Extraction

echo "🚀 Setting up MongoDB for Video Face Extraction..."

# Function to detect Docker Compose command
get_docker_compose_cmd() {
    if command -v docker-compose >/dev/null 2>&1; then
        echo "docker-compose"
    elif docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    else
        echo ""
    fi
}

# Function to check if MongoDB is running
check_mongodb() {
    if command -v mongosh >/dev/null 2>&1; then
        mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1
        return $?
    elif command -v mongo >/dev/null 2>&1; then
        mongo --eval "db.adminCommand('ping')" >/dev/null 2>&1
        return $?
    else
        return 1
    fi
}

# Check if running in Docker environment
if [ -f "/.dockerenv" ]; then
    echo "📦 Running in Docker environment"
    MONGO_URI="mongodb://admin:adminpassword@mongodb:27017/video_faces?authSource=admin"
else
    echo "💻 Running in local environment"
    MONGO_URI="mongodb://localhost:27017/video_faces"
fi

# Get Docker Compose command
DOCKER_COMPOSE_CMD=$(get_docker_compose_cmd)
if [ -z "$DOCKER_COMPOSE_CMD" ]; then
    echo "❌ Docker Compose not found. Please install Docker Compose or Docker with Compose plugin"
    echo "   Installation options:"
    echo "   1. Docker Desktop (includes compose plugin)"
    echo "   2. Docker Compose standalone: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Using Docker Compose command: $DOCKER_COMPOSE_CMD"

echo "1. Starting MongoDB with Docker Compose..."
cd /home/farkhane/mini-rag/docker
$DOCKER_COMPOSE_CMD up -d mongodb

echo "2. Waiting for MongoDB to be ready..."
timeout=60
elapsed=0
while ! $DOCKER_COMPOSE_CMD exec mongodb mongosh --eval "db.adminCommand('ping')" >/dev/null 2>&1; do
    if [ $elapsed -ge $timeout ]; then
        echo "❌ MongoDB failed to start within $timeout seconds"
        echo "🔍 Troubleshooting steps:"
        echo "   1. Check Docker status: docker ps"
        echo "   2. Check MongoDB logs: $DOCKER_COMPOSE_CMD logs mongodb"
        echo "   3. Check MongoDB container: $DOCKER_COMPOSE_CMD ps mongodb"
        exit 1
    fi
    echo "   Waiting for MongoDB... ($elapsed/$timeout seconds)"
    sleep 2
    elapsed=$((elapsed + 2))
done

echo "3. MongoDB is ready! 🎉"

echo "4. Initializing MongoDB collections and indexes..."
python init_mongodb.py

echo "5. Installing Python dependencies..."
cd /home/farkhane/mini-rag
pip install -r src/requirements.txt

echo "📋 Setup Summary:"
echo "   - MongoDB: Running on port 27017"
echo "   - Database: video_faces"
echo "   - Collection: frames"
echo "   - Connection URI: $MONGO_URI"
echo ""
echo "🎬 Next steps:"
echo "   1. Place your video file in src/assets/"
echo "   2. Update VIDEO_PATH in src/assets/video_face_extractor.py"
echo "   3. Run: python src/assets/video_face_extractor.py"
echo ""
echo "🔍 MongoDB Management:"
echo "   - View logs: $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml logs mongodb"
echo "   - Connect: $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml exec mongodb mongosh -u admin -p adminpassword"
echo "   - Stop: $DOCKER_COMPOSE_CMD -f docker/docker-compose.yml stop mongodb"
