#!/usr/bin/env python3
"""
MongoDB Management Script for Video Face Extraction
"""

import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), 'docker/env/.env.mongodb'))

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DATABASE", "video_faces")

def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        client = MongoClient(MONGO_URI)
        db = client[DB_NAME]
        # Test connection
        client.admin.command('ping')
        return client, db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        return None, None

def show_stats():
    """Show database statistics"""
    client, db = connect_to_mongodb()
    if not client:
        return
    
    try:
        frames_col = db.frames
        total_frames = frames_col.count_documents({})
        frames_with_faces = frames_col.count_documents({"face_found": True})
        frames_without_faces = frames_col.count_documents({"face_found": False})
        
        print("📊 Database Statistics:")
        print(f"   Total frames: {total_frames}")
        print(f"   Frames with faces: {frames_with_faces}")
        print(f"   Frames without faces: {frames_without_faces}")
        
        if total_frames > 0:
            success_rate = (frames_with_faces / total_frames) * 100
            print(f"   Face detection success rate: {success_rate:.2f}%")
            
    except Exception as e:
        print(f"❌ Error getting stats: {e}")
    finally:
        client.close()

def clear_database():
    """Clear all data from the database"""
    client, db = connect_to_mongodb()
    if not client:
        return
        
    try:
        confirm = input("⚠️  Are you sure you want to clear all data? (yes/no): ")
        if confirm.lower() == 'yes':
            result = db.frames.delete_many({})
            print(f"✅ Deleted {result.deleted_count} documents")
        else:
            print("Operation cancelled")
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
    finally:
        client.close()

def list_recent_frames(limit=10):
    """List recent frames"""
    client, db = connect_to_mongodb()
    if not client:
        return
        
    try:
        frames_col = db.frames
        recent_frames = frames_col.find().sort("_id", -1).limit(limit)
        
        print(f"📋 Recent {limit} frames:")
        for frame in recent_frames:
            status = "✅" if frame.get("face_found") else "❌"
            print(f"   {status} Frame {frame['frame_number']}: {os.path.basename(frame['frame_path'])}")
            
    except Exception as e:
        print(f"❌ Error listing frames: {e}")
    finally:
        client.close()

def main():
    if len(sys.argv) < 2:
        print("🔧 MongoDB Management for Video Face Extraction")
        print("Usage:")
        print("  python mongo_manager.py stats     - Show database statistics")
        print("  python mongo_manager.py clear     - Clear all data")
        print("  python mongo_manager.py list [N]  - List recent N frames (default: 10)")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        show_stats()
    elif command == "clear":
        clear_database()
    elif command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_recent_frames(limit)
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
