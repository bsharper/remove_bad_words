import re
import os
import sys
import math
import signal
from subprocess import Popen, PIPE, run, CalledProcessError
try:
    from alive_progress import alive_bar
except:
    from fake_progress import LineUpdate as alive_bar


verbose = False
if "DEBUG" in os.environ.keys() and os.environ["DEBUG"] == 1:
    verbose = True

def get_media_duration(file_path):
    """
    Get the duration of a media file using ffmpeg.
    """
    try:
        result = run(f"ffmpeg -i \"{file_path}\" 2>&1 | grep \"Duration\"", 
                                shell=True, check=True, text=True, capture_output=True)
        return re.match(r'\s*Duration: (\d\d:\d\d:\d\d.\d\d)', result.stdout)[1]
    except CalledProcessError as e:
        return f"Error: {e}"

def convert_time_to_seconds(time_str):
    """
    Convert a time string in the format HH:MM:SS.sss to seconds.
    """
    try:
        hours, minutes, seconds = time_str.split(":")
        totalSeconds = (int(hours) * 3600) + (int(minutes) * 60) + float(seconds)
        return totalSeconds
    except ValueError:
        return 0

def run_transcription_process(whisper_path, model_path, audio_path):
    """
    Run the external transcription process and monitor its output.
    """
    if not os.path.exists(audio_path):
        print (f'Audio file "{audio_path}" does not exist')
        sys.exit(2)
    
    if not all([ os.path.exists(x) for x in [whisper_path, model_path] ]):
        print (f"whisper binary or model could not be found, please check the path and try again")
        sys.exit(3)

    args = [whisper_path, '-m', model_path, '--split-on-word', '-ng', '-otxt', '-osrt', '-ojf', audio_path]
    if verbose: print (f"> {' '.join(args)}")
    process = Popen(args, stdout=PIPE, stderr=PIPE, text=True)

    #total_duration = get_media_duration(audio_path)
    #total_duration_seconds = int(convert_time_to_seconds(total_duration))
    
    for line in iter(process.stderr.readline, ''):
        m = re.match('main:.* (\d+\.\d+) sec', line)
        if m:
            total_duration = float(m[1])
            total_duration_seconds = int(math.ceil(total_duration))
            break
    try:
        with alive_bar(total_duration_seconds, manual=True, title=f'Running whisper on "{audio_path}"') as bar:
            for line in iter(process.stdout.readline, ''):
                txt=""
                if "]" in line:
                    txt = line.split("]")[1].strip()
                    #txt = f"current text: {txt}"
                
                match = re.search(r'\[\d{2}:\d{2}:\d{2}\.\d{3} --> (\d{2}:\d{2}:\d{2}\.\d{3})\]', line)

                if match:
                    current_time = match.group(1)
                    current_time_seconds = convert_time_to_seconds(current_time)

                    
                    per = (current_time_seconds / total_duration_seconds)
                    bar(per)
                    bar.text(txt)
            bar(1)

    except Exception as e:
        print(f"Error during transcription: {e}")
    finally:
        process.stdout.close()


def signal_handler(sig, frame):
    print('Ctrl+C detected, exiting')
    sys.exit(1)

if __name__== "__main__":
    args = sys.argv[1:]
    if len(args) != 3:
        print ("Need 3 arguments: whisper.cpp/main path, model path, and audio file path")
        sys.exit(1)
    whisper_path = args[0]
    model_path = args[1]
    audio_path = args[2]
    signal.signal(signal.SIGINT, signal_handler)
    run_transcription_process(whisper_path, model_path, audio_path)
