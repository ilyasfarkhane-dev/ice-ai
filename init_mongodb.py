#!/usr/bin/env python3
"""
Initialize MongoDB collections and indexes for video face extraction
"""

import asyncio
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'docker/env/.env.mongodb'))

async def init_mongodb():
    """Initialize MongoDB collections and indexes"""
    try:
        # Connect to MongoDB
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO_DATABASE", "video_faces")
        
        client = AsyncIOMotorClient(mongo_uri)
        db = client[db_name]
        
        print(f"🔗 Connecting to MongoDB: {db_name}")
        
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connection successful")
        
        # Create collections
        videos_col = db.videos
        frames_col = db.frames
        
        # Create indexes for videos collection
        print("📊 Creating indexes for videos collection...")
        await videos_col.create_index("status")
        await videos_col.create_index("created_at")
        await videos_col.create_index("filename")
        
        # Create indexes for frames collection
        print("📊 Creating indexes for frames collection...")
        await frames_col.create_index("video_id")
        await frames_col.create_index("frame_number")
        await frames_col.create_index("face_found")
        await frames_col.create_index([("video_id", 1), ("frame_number", 1)])
        await frames_col.create_index([("video_id", 1), ("face_found", 1)])
        
        print("✅ MongoDB initialization completed successfully!")
        print(f"   Database: {db_name}")
        print(f"   Collections: videos, frames")
        print(f"   Indexes: Created for optimal query performance")
        
        # Show collection stats
        videos_count = await videos_col.count_documents({})
        frames_count = await frames_col.count_documents({})
        
        print(f"\n📈 Current data:")
        print(f"   Videos: {videos_count}")
        print(f"   Frames: {frames_count}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error initializing MongoDB: {e}")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(init_mongodb())
