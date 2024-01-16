import pynput
from main import MainThread

END_KEY = pynput.keyboard.Key.f8

main_thread = MainThread()

# should it cap to x amount of time
# main_thread.seconds = 30
main_thread.use_time_cap = False
main_thread.start()

def end(key):
    if key == END_KEY:
        # Need to do three things:
        # stop listening
        # save file
        # transcribe last heard words
        main_thread.run_flag = False
        main_thread.join()
        print()
        print("*" * 10)
        print(f"output:\n\n{main_thread.total_transcription}")
        print("*" * 10)
        exit()

key_listener = pynput.keyboard.Listener(on_press=end)
key_listener.start()
