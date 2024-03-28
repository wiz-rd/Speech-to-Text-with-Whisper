#!/usr/bin/python3
import argparse
import os
from keyhandler import main as kh_main, transcribe as kh_transcribe
from pynput.keyboard import Key

def main():
    parser = argparse.ArgumentParser(description="A simple interface for Whisper that allows conversations to be recorded and transcribed in segments.")
    parser.add_argument("-f", "--file", help="The path for the output transcription.")
    parser.add_argument("-o", "--overwrite", help="Overwrites the input file with a new recording. Defaults to false.", default=False, action="store_true")
    parser.add_argument("-d", "--duration", help="The duration for the rolling time option. Can be float or int.", default=30)
    parser.add_argument("-e", "--endkey", help="The key to end listening and begin transcribing. Defaults to f4.", default=Key.f4)
    parser.add_argument("-m", "--model", help="The Whisper model to use. Defaults to 'medium.'", default="medium", type=str)

    recording_type = parser.add_mutually_exclusive_group(required=True)
    recording_type.add_argument("-s", "--source", help="The file to transcribe. Use this if you don't want to record anything. Will disable overwriting if so.")
    recording_type.add_argument("-r", "--rolling", help="Whether or not to record and transcribe in segments. Defaults to 30 seconds per segment. Each segment will be overwritten if not specified.", default=False, action="store_true")
    recording_type.add_argument("-i", "--indefinite", help="Records until the endkey (default f4) is pressed.", action="store_true")

    args = parser.parse_args()

    source = args.source
    file = args.file
    overwrite = args.overwrite
    rolling = args.rolling
    duration = args.duration
    end_key = args.endkey
    model = args.model

    # if duration is neither float nor int...
    if type(duration) != float and type(duration) != int:
        # exit the code
        parser.error(f"The duration given was not an int or float. It is a {type(duration)}")

    # if a source is given
    if source:
        overwrite = False
        # but it doesn't exist...
        while not os.path.exists(source):
            # demand a source
            source = input("A source audio file is necessary. Please provide a path here or press Ctrl+C to exit: ")

    # if no output file is given...
    # handling an output file
    if file is None:
        file = input("If you would like to store the output transcription into a file, put the filename here [file/n]: ")
        # if n is selected
        if file == "n":
            file = None
        # so long as the path does not exist...
        else:
            while True:
                # confirm that the file exists
                if not os.path.exists(file):
                    file = input("That path does not exist or cannot be accessed. Please provide another one [file/n]: ")
                    if file == "n":
                        file = None
                        break
                else:
                    break


    if not source:
        kh_main(overwrite, duration, rolling, model, end_key)
    else:
        transcription = kh_transcribe(source)
        print(transcription)
        # TODO: replace this with whatever I would like to do with the text. Right now,
        # I just want to see it, but I'm planning to do more.

        # writes the transcription to a file if an output file was chosen
        if file:
            with open(file, "r+") as output_transcription:
                output_transcription.write(transcription)


if __name__ == "__main__":
    main()
