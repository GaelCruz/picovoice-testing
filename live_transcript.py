import pvcheetah
from pvrecorder import PvRecorder

ACCESS_KEY = "oTgITbKOCV8fbVN+HA6trEDMUUVHYO1Q/MoVu39OTQsNfAMQfxWbHQ=="

cheetah = pvcheetah.create(ACCESS_KEY)


for index, name in enumerate(PvRecorder.get_available_devices()):
  print('Device #%d: %s' % (index, name))


try:
  # Create a new PvRecorder instance
  recorder = PvRecorder(frame_length=512, device_index=0)
  
  # Start the recorder
  recorder.start()
  
  # Print instructions
  print("Press Ctrl+C to stop the recorder")
  print("Listening...")
  
  try:
    # Get the current frame
    frame = recorder.read()
    
    #listen/process frames
    while True:
      # Process the frame
      partial_transcript, is_endpoint = cheetah.process(frame)
      
      #Print the partial transcript
      print(partial_transcript, end='', flush=True)
      
      if is_endpoint:
        final_transcript = cheetah.flush()
        print(final_transcript)
  finally:
    print()
    recorder.stop()
except KeyboardInterrupt:
  pass
except CheetahActivationLimitError:
  print("Activation limit exceeded. Please try again later.")
finally:
  print("Stopping the recorder...")
  cheetah.delete
