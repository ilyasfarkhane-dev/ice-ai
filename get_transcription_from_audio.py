#!/usr/bin/env python3
"""
Quick script to get transcription from existing audio file
Since the API lost the database, this extracts results from the saved audio file
"""

import whisper
import os

# Path to your successfully extracted audio
audio_file = "/home/farkhane/mini-rag/src/assets/audio/video_0064db68-b3cf-44a8-9fcf-d62716938c6b_audio.wav"

print("🎬 Getting transcription from existing audio file...")
print(f"📁 Audio file: {audio_file}")

# Check if file exists
if not os.path.exists(audio_file):
    print("❌ Audio file not found!")
    exit(1)

print(f"📊 File size: {os.path.getsize(audio_file) / 1024 / 1024:.1f} MB")

# Load Whisper model
print("🤖 Loading Whisper model...")
model = whisper.load_model("base")

# Transcribe
print("🗣️ Transcribing speech...")
result = model.transcribe(audio_file)

# Format results exactly like your API
print("\n" + "="*60)
print("✅ TRANSCRIPTION RESULTS")
print("="*60)

formatted_transcription = []
for segment in result['segments']:
    start_time = segment['start']
    end_time = segment['end']
    text = segment['text'].strip()
    
    formatted_line = f"[{start_time:.2f}s - {end_time:.2f}s]: {text}"
    formatted_transcription.append(formatted_line)
    print(formatted_line)

print("\n" + "="*60)
print(f"📊 SUMMARY:")
print(f"   Total segments: {len(formatted_transcription)}")
print(f"   Total duration: {result['segments'][-1]['end']:.2f} seconds")
print(f"   Video ID was: 0064db68-b3cf-44a8-9fcf-d62716938c6b")
print("="*60)

# Save to file
output_file = "/home/farkhane/mini-rag/transcription_results.txt"
with open(output_file, 'w') as f:
    f.write("TRANSCRIPTION RESULTS\n")
    f.write("="*60 + "\n")
    for line in formatted_transcription:
        f.write(line + "\n")
    f.write("\n" + "="*60 + "\n")
    f.write(f"Total segments: {len(formatted_transcription)}\n")
    f.write(f"Total duration: {result['segments'][-1]['end']:.2f} seconds\n")

print(f"💾 Results saved to: {output_file}")
