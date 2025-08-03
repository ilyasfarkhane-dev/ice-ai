import cv2
import os
from PIL import Image
from tqdm import tqdm
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '../../docker/env/.env.mongodb'))

# --- CONFIG ---
VIDEO_PATH = "your_video.mp4"  
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "full_frames")
FACES_DIR = os.path.join(os.path.dirname(__file__), "faces_cropped")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DATABASE", "video_faces")
COLLECTION_NAME = "frames"
FRAME_INTERVAL = 30

# --- SETUP ---
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(FACES_DIR, exist_ok=True)

# --- MONGODB ---
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
frames_col = db[COLLECTION_NAME]

# --- EXTRACT FRAMES ---
def extract_frames():
    cap = cv2.VideoCapture(VIDEO_PATH)
    frame_count = 0
    saved_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_count % FRAME_INTERVAL == 0:
            filename = os.path.join(ASSETS_DIR, f"frame_{saved_count:04d}.jpg")
            cv2.imwrite(filename, frame)
            frames_col.insert_one({
                "frame_number": frame_count,
                "frame_path": filename,
                "face_path": None,
                "face_found": False
            })
            saved_count += 1
        frame_count += 1
    cap.release()
    print(f"Saved {saved_count} full-size frames to {ASSETS_DIR}")

# --- FACE DETECTION ---
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)
def extract_face(src_path, dst_path):
    img = cv2.imread(src_path)
    if img is None:
        return False
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
    if len(faces) == 0:
        return False
    x, y, w, h = faces[0]
    margin = 20
    x = max(x - margin, 0)
    y = max(y - margin, 0)
    w = min(w + 2*margin, img.shape[1] - x)
    h = min(h + 2*margin, img.shape[0] - y)
    face_rgb = cv2.cvtColor(img[y:y+h, x:x+w], cv2.COLOR_BGR2RGB)
    Image.fromarray(face_rgb).save(dst_path)
    return True

def process_faces():
    for doc in tqdm(list(frames_col.find()), desc="Processing images"):
        src_file = doc["frame_path"]
        fname = os.path.basename(src_file)
        dst_file = os.path.join(FACES_DIR, os.path.splitext(fname)[0] + "_face.jpg")
        found = extract_face(src_file, dst_file)
        frames_col.update_one({"_id": doc["_id"]}, {"$set": {"face_path": dst_file if found else None, "face_found": found}})
    print("✅ Face extraction complete.")

if __name__ == "__main__":
    extract_frames()
    process_faces()
