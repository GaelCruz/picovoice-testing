import pvcheetah
from pvrecorder import PvRecorder

ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="

cheetah = pvcheetah.create(ACCESS_KEY)

for index, name in enumerate(PvRecorder.get_available_devices()):
    print('Device #%d: %s' % (index, name))

try:
    recorder = PvRecorder(frame_length=512, device_index=0)
    recorder.start()
    print("Press Ctrl+C to stop the recorder")
    print("Listening...")

    try:
        while True:
            frame = recorder.read()
            partial_transcript, is_endpoint = cheetah.process(frame)
            print(partial_transcript, end='', flush=True)
            if is_endpoint:
                final_transcript = cheetah.flush()
                print(final_transcript)
                # Print a new line to separate each endpoint
                print("\n", end='', flush=True)
    except KeyboardInterrupt:
        print("Recording stopped by user")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        recorder.stop()
except pvcheetah.CheetahActivationLimitError:
    print("Activation limit exceeded. Please try again later.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    cheetah.delete()
