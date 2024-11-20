import pvcheetah
from pvcheetah import CheetahActivationLimitError
from pvrecorder import PvRecorder
from enroll import enroll_speaker, cleanup
import pveagle
import json
import os
import time
import threading

ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="
PROFILE_FILE = "speaker_profiles.json"

# Load the saved speaker profiles from JSON
if os.path.exists(PROFILE_FILE):
    with open(PROFILE_FILE, "r") as f:
        speaker_profiles_dict = json.load(f)
    speaker_profiles = [pveagle.EagleProfile.from_bytes(profile.encode('latin1')) for profile in speaker_profiles_dict.values()]
    speaker_ids = list(speaker_profiles_dict.keys())
else:
    print("No speaker profiles found. Please enroll speakers first.")
    exit(1)

cheetah = pvcheetah.create(ACCESS_KEY, endpoint_duration_sec=1.0)

for index, name in enumerate(PvRecorder.get_available_devices()):
    print('Device #%d: %s' % (index, name))

try:
    print('Cheetah version : %s' % cheetah.version)

    recorder = PvRecorder(frame_length=cheetah.frame_length, device_index=0)
    recorder.start()
    print('Listening... (press Ctrl+C to stop)')

    eagle = pveagle.create_recognizer(access_key=ACCESS_KEY, speaker_profiles=speaker_profiles)

    def animate_loading():
        for _ in range(10):  # Adjust the range for the desired duration
            for dots in range(4):
                print("\rListening for the speaker" + "." * dots, end="", flush=True)
                time.sleep(0.5)
        print("\r" + " " * 30, end="", flush=True)  # Clear the loading line

    try:
        while True:
            partial_transcript, is_endpoint = cheetah.process(recorder.read())
            print(partial_transcript, end='', flush=True)
            if is_endpoint:
                final_transcript = cheetah.flush()
                print(final_transcript)
                
                if final_transcript.lower() == 'enroll new user':
                    print("\nPlease state your username...")
                    
                    user_type = ""
                    
                    while(user_type == ""):
                        partial_transcript, is_endpoint = cheetah.process(recorder.read())
                        print(partial_transcript, end='', flush=True)
                        if is_endpoint:
                            final_transcript = cheetah.flush()
                            print(final_transcript)
                            user_type = final_transcript.lower()
                    
                    enroll_speaker(user_type)
                    print(f"{user_type.capitalize()} profile has been enrolled.")
                
                elif final_transcript.lower() == 'who is speaking':
                    print("Please speak for a few seconds...")

                    # Start loading animation
                    loading_thread = threading.Thread(target=animate_loading)
                    loading_thread.start()
                    
                    # Collect audio for a few seconds
                    audio_frames = []
                    start_time = time.time()
                    duration = 5  # Duration in seconds
                    while time.time() - start_time < duration:
                        frame = recorder.read()
                        audio_frames.extend(frame)
                    
                    # Ensure the loading animation stops
                    loading_thread.join()

                    # Process the collected audio frames
                    scores = eagle.process(audio_frames[:eagle.frame_length])
                    print("Scores:", scores)  # Debugging line to check scores
                    
                    # Determine the highest score
                    max_score_index = scores.index(max(scores))
                    identified_speaker = speaker_ids[max_score_index]
                    print(f"The speaker is identified as: {identified_speaker.capitalize()}")
    
    finally:
        recorder.stop()
except KeyboardInterrupt:
    pass
except CheetahActivationLimitError:
    print('AccessKey has reached its processing limit.')
finally:
    cleanup()
    cheetah.delete()
    eagle.delete()
