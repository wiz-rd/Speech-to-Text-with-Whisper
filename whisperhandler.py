from collections.abc import Callable, Iterable, Mapping
import os
import queue
import threading
from time import time
from typing import Any

import whisper
import sounddevice as sd
import soundfile as sf
import numpy
assert numpy

class WhisperHandler(threading.Thread):
    def __init__(self, output_file_path = "output.wav", overwrite = True, seconds_to_record = 30, use_time_cap = True, model = "medium", model_path = "models/", sample_rate = 44100, group: None = None, target: Callable[..., object] | None = None, name: str | None = None, args: Iterable[Any] = ..., kwargs: Mapping[str, Any] | None = None, *, daemon: bool | None = None) -> None:
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        """
        An interface for creating recordings and then transcribing said recordings in a psuedo-live manner.
        """
        self.sample_rate = sample_rate
        self.seconds = seconds_to_record
        self.output_file = output_file_path
        self.model = whisper.load_model(model, download_root=model_path)
        self.overwrite = overwrite
        self.use_time_cap = use_time_cap

        self.total_transcription = ""

        self.q = queue.Queue()

        self.run_flag = True


    def transcribe(self, file: str):
        print("transcription of file start")
        now = time()

        if not os.path.exists(self.output_file):
            return {"text": "no file to transcribe"}

        result = self.model.transcribe(file)

        length = time() - now
        print(f"transcription of previous file end: {length}")

        self.total_transcription += result["text"]


        return result


    # a kind of odd method recommended/written by the sounddevice dev
    def callback_for_sound(self, indata, frames, time, status):
        if status:
            print(status)
        
        self.q.put(indata.copy())


    # should override the normal Threading run,
    # and as such, should be ran when the thread is started.
    def run(self):

        use_counter = (not self.overwrite) and self.use_time_cap

        if use_counter:
            counter = 0
        else:
            counter = ""

        # run_flag will allow this to be exited upon run_flag == False
        while self.run_flag:

            # deleting the old recording...
            if os.path.exists(counter + self.output_file) and self.overwrite:
                os.remove(counter + self.output_file)

            # print(f"recording next {seconds} seconds to {output_file}")
            print("part start") if self.use_time_cap else print("listening")

            # listen "indefinitely" - actually just waits until the length of time is reached,
            # and then exits the loop.
            with sf.SoundFile(counter + self.output_file, mode="x", samplerate=self.sample_rate, channels=2) as file:

                with sd.InputStream(samplerate=self.sample_rate, channels=2, callback=self.callback_for_sound):
                    now = time()

                    while self.overwrite == True:
                        file.write(self.q.get())

                        # if it's been over the threshold (and the threshold is used)...
                        # export and then transcribe the sounds
                        # OR if it's been told to end the thread
                        if (time() - now > self.seconds and self.use_time_cap) or (not self.run_flag):
                            break
                    

            # perform whisper of previous file here if it exists
            # if no other files exist, wait
            self.transcribe(counter + self.output_file)

            # print(f"saving new output to {output_file}")
            print("part complete")

            if use_counter:
                counter += 1
        
        self.total_transcription = self.total_transcription.strip()
