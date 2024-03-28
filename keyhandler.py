#!/usr/bin/python3
from pathlib import Path
import pynput
from whisperhandler import WhisperHandler

END_KEY = pynput.keyboard.Key.f4

def main(overwrite: bool = False, duration: int | float = 30, rolling: bool = False, model: str = "medium", end_key = END_KEY):
    """
    Records, saves, and then transcribes audio from the microphone.
    """
    main_thread = WhisperHandler(overwrite=overwrite, seconds_to_record=duration, use_time_cap=rolling, model=model)

    # should it cap to x amount of time
    main_thread.seconds = duration
    main_thread.use_time_cap = rolling
    main_thread.start()

    def end(key):
        if key == end_key:
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

    key_listener.join()


def transcribe(input_file: str | Path) -> str:
    """
    Transcribes a file WITHOUT listening by importing WhisperHandler
    """

    main_thread = WhisperHandler()

    output = main_thread.transcribe(input_file)["text"]

    return output


if __name__ == "__main__":
    main()

