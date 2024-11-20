import pvcheetah 
from pvcheetah import CheetahActivationLimitError
from pvrecorder import PvRecorder

ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="

cheetah = pvcheetah.create(ACCESS_KEY, endpoint_duration_sec=1.0)

for index, name in enumerate(PvRecorder.get_available_devices()):
    print('Device #%d: %s' % (index, name))

try:
        print('Cheetah version : %s' % cheetah.version)

        recorder = PvRecorder(frame_length=cheetah.frame_length, device_index=0)
        recorder.start()
        print('Listening... (press Ctrl+C to stop)')

        try:
            while True:
                partial_transcript, is_endpoint = cheetah.process(recorder.read())
                print(partial_transcript, end='', flush=True)
                if is_endpoint:
                    final_transcript=cheetah.flush()
                    print(final_transcript)
                    
                    if(final_transcript.lower() == 'red light'):
                        print("RED LIGHT DETECTED.")
                    
        finally:
            print()
            recorder.stop()

except KeyboardInterrupt:
        pass
except CheetahActivationLimitError:
        print('AccessKey has reached its processing limit.')
finally:
        cheetah.delete()
