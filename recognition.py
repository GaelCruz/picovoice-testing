import pveagle
from pvrecorder import PvRecorder
import time
import os
import json

# RECOGNITION
ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="
PROFILE_FILE = "speaker_profiles.json"

# Load the saved speaker profiles from JSON
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        speaker_profiles_dict = json.load(f)
    speaker_profiles = [pveagle.EagleProfile.from_bytes(profile.encode('latin1')) for profile in speaker_profiles_dict.values()]
else:
    print("No speaker profiles found. Please enroll speakers first.")
    exit(1)

print("Speaker Profiles Loaded:", speaker_profiles)

try:
    eagle = pveagle.create_recognizer(
        access_key=ACCESS_KEY,
        speaker_profiles=speaker_profiles)
except pveagle.EagleError as e:
    # Handle error
    print(f"Error creating recognizer: {e}")
    exit(1)

DEFAULT_DEVICE_INDEX = 0
recorder = PvRecorder(
    device_index=DEFAULT_DEVICE_INDEX,
    frame_length=eagle.frame_length)

try:
    recorder.start()
except Exception as e:
    # Handle error
    print(f"Error starting recorder: {e}")
    eagle.delete()
    exit(1)

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_bars(scores, max_length=50):
    clear_console()
    print("Recognition Scores")
    print("==================")
    for i, score in enumerate(scores):
        bar_length = int(score * max_length)
        bar = '=' * bar_length
        print(f"Speaker {i + 1}: [{bar:<{max_length}}] {score:.2f}")

print("Recognition started. Press Ctrl+C to stop.")
try:
    while True:
        audio_frame = recorder.read()
        scores = eagle.process(audio_frame)
        print("Scores:", scores)  # Debugging line to check scores
        display_bars(scores)
        time.sleep(0.1)  # Adjust the sleep time as necessary
except KeyboardInterrupt:
    print("Recognition stopped by user.")
finally:
    recorder.stop()
    recorder.delete()
    eagle.delete()
