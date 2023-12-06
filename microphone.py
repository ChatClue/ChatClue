import argparse
import queue
import sys
import json
import os
import threading
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from openai import OpenAI

q = queue.Queue()
response_queue = queue.Queue()
stop_signal = threading.Event()
client = OpenAI()
quiet_please_phrases = [
    "be noiseless", "button it", "calm your voice", "cease speaking", 
    "cease your chatter", "close your mouth", "cut it out", "don't speak", 
    "end the noise", "enough", "go mute", "hush", "hush down", 
    "hush now", "keep quiet", "keep it down", "keep the silence", "mum's the word", 
    "mute", "muzzle it", "no chit chat", "no more words", "no talking", 
    "not another word", "please stop", "put a lid on it", "quiet", "quietude", 
    "shh", "shhh", "shut up", "silence", "silence yourself", "silence your lips", 
    "speechless", "sshh", "stay mum", "stifle your speech", "stop", "stop babbling", 
    "stop blabbering", "stop talking", "tone it down"
]


def int_or_str(text):
    """Helper function for argument parsing."""
    try:
        return int(text)
    except ValueError:
        return text

def callback(indata, frames, time, status):
    """This is called (from a separate thread) for each audio block."""
    if status:
        print(status, file=sys.stderr)
    q.put(bytes(indata))

def contains_quiet_please_phrase(input_string):
    for phrase in quiet_please_phrases:
        if phrase in input_string:
            return True
    return False

def openai_stream(recognized_text, stop_signal):
    response = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[
            {'role': 'user', 'content': recognized_text}
        ],
        temperature=0,
        stream=True
    )
    for chunk in response:
        if stop_signal.is_set():
            break
        response_queue.put(chunk)


parser = argparse.ArgumentParser(add_help=False)
parser.add_argument(
    "-l", "--list-devices", action="store_true",
    help="show list of audio devices and exit")
args, remaining = parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[parser])
parser.add_argument(
    "-f", "--filename", type=str, metavar="FILENAME",
    help="audio file to store recording to")
parser.add_argument(
    "-d", "--device", type=int_or_str,
    help="input device (numeric ID or substring)")
parser.add_argument(
    "-r", "--samplerate", type=int, help="sampling rate")
parser.add_argument(
    "-m", "--model", type=str, help="language model; e.g. en-us, fr, nl; default is en-us")
args = parser.parse_args(remaining)

try:
    if args.samplerate is None:
        device_info = sd.query_devices(args.device, "input")
        args.samplerate = int(device_info["default_samplerate"])
        
    if args.model is None:
        model = Model(lang="en-us")
    else:
        model = Model(lang=args.model)

    if args.filename:
        dump_fn = open(args.filename, "wb")
    else:
        dump_fn = None

    with sd.RawInputStream(samplerate=args.samplerate, blocksize = 28000, device=args.device,
                           dtype="int16", channels=1, callback=callback):
        print("#" * 80)
        print("Press Ctrl+C to stop the recording")
        print("#" * 80)

        rec = KaldiRecognizer(model, args.samplerate)
        openai_stream_thread = None
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())["text"]
                if result != '':
                    print(result)
                    print("")
                    if "robot" in result.lower():
                        if not openai_stream_thread or not openai_stream_thread.is_alive():
                            stop_signal.clear()  # Reset the signal for a new request
                            openai_stream_thread = threading.Thread(target=openai_stream, args=(result, stop_signal))
                            openai_stream_thread.start()
                    else:
                        print("I'm just listening to your conversation :)")
                        print("")
            partial_result_json = json.loads(rec.PartialResult())
            if 'partial' in partial_result_json and contains_quiet_please_phrase(partial_result_json['partial']):
                # Signal to stop the current OpenAI stream
                print("Okay, I'll be quiet")
                stop_signal.set() 
                with response_queue.mutex:
                    response_queue.queue.clear()

            if dump_fn is not None:
                dump_fn.write(data)


            while not response_queue.empty():
                chunk = response_queue.get()
                if chunk.choices[0].delta.content is not None:
                    print(chunk.choices[0].delta.content, end='')

except KeyboardInterrupt:
    print("\nDone")
    parser.exit(0)
except Exception as e:
    parser.exit(type(e).__name__ + ": " + str(e))
