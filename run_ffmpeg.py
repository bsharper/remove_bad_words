import re
import os
import sys
import math
try:
    from alive_progress import alive_bar
except:
    from fake_progress import LineUpdate as alive_bar

from subprocess import Popen, PIPE, DEVNULL, run, CalledProcessError

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


def get_media_duration(file_path):
    """
    Get the duration of a media file using ffmpeg.
    """
    try:
        result = run(f"ffmpeg -i \"{file_path}\" 2>&1 | grep \"Duration\"", 
                                shell=True, check=True, text=True, capture_output=True)
        return convert_time_to_seconds(re.match(r'\s*Duration: (\d\d:\d\d:\d\d.\d\d)', result.stdout)[1])
    except CalledProcessError as e:
        return f"Error: {e}"

def main():
    args = sys.argv[1:]
    if len(args) == 0:
        print ("Arguments missing.")
        sys.exit(1)
    
    verbose = False
    if "DEBUG" in os.environ.keys() and os.environ["DEBUG"] == 1:
        verbose = True

    input_filename = ""
    output_filename = ""
    duration = 0
    args.insert(0, 'ffmpeg')
    if "-y" not in args:
        args.append("-y")
    if verbose: print (f"> {' '.join(args)}")
    process = Popen(args, stdout=PIPE, stderr=PIPE, stdin=PIPE, text=True)
    for line in iter(process.stderr.readline, ''):
        m = re.match(r'\s*Duration: (\d\d:\d\d:\d\d.\d\d)', line)
        if m:
            duration = int(math.ceil(convert_time_to_seconds(m[1])))
            if duration and input_filename and output_filename:
                break
        im = re.match("Input #\d,.*from '(.*)'", line)
        if im:
            if input_filename:
                input_filename = f"{input_filename},{im[1]}"
            else:
                input_filename = im[1]

            if duration and input_filename and output_filename:
                break
        om = re.match("Output #0,.*to '(.*)'", line)
        if om:
            output_filename = om[1]
            if duration and input_filename and output_filename:
                break
        # if duration == 0:
        #     print (line)
        #print (duration, input_filename, output_filename)
        
    
    title = f'Converting "{input_filename}" to "{output_filename}"'
    with alive_bar(duration, manual=True, title=title) as bar:
        for line in iter(process.stderr.readline, ''):
            m = re.match('.*time=(\d\d:\d\d:\d\d\.\d+)', line)
            if m:
                time = m[1]
                seconds = convert_time_to_seconds(time)
                per = seconds/duration
                bar(per)
        bar(1)

if __name__ == "__main__":
    main()