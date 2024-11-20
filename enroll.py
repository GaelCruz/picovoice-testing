# enroll.py
import pveagle
from pvrecorder import PvRecorder
import json
import os

ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="
PROFILE_FILE = "speaker_profiles.json"

# Load existing profiles
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        speaker_profiles = json.load(f)
else:
    speaker_profiles = {}

try:
    eagle_profiler = pveagle.create_profiler(access_key=ACCESS_KEY)
except pveagle.EagleError as e:
    # Handle error
    print(f"Error creating profiler: {e}")
    exit(1)

DEFAULT_DEVICE_INDEX = 0
recorder = PvRecorder(
    device_index=DEFAULT_DEVICE_INDEX,
    frame_length=eagle_profiler.min_enroll_samples)

try:
    recorder.start()
except Exception as e:
    # Handle error
    print(f"Error starting recorder: {e}")
    eagle_profiler.delete()
    exit(1)

def enroll_speaker(speaker_type):
    enroll_percentage = 0.0
    while enroll_percentage < 100.0:
        audio_frame = recorder.read()
        enroll_percentage, feedback = eagle_profiler.enroll(audio_frame)
        print(f"Enrollment progress: {enroll_percentage}% - Feedback: {feedback}")

    # Save the speaker profile
    speaker_profiles[speaker_type] = eagle_profiler.export().to_bytes().decode('latin1')
    
    # Save the updated profiles
    with open(PROFILE_FILE, "w") as f:
        json.dump(speaker_profiles, f)

    print(f"Speaker {speaker_type} enrolled and saved.")

# Call recorder.stop() and eagle_profiler.delete() after enrollment
def cleanup():
    recorder.stop()
    eagle_profiler.delete()
