import sys
import json
import wave
import contextlib
import numpy as np

def parse_time(time_str):
    """Converts time from 'HH:MM:SS,ms' format to seconds."""
    h, m, s = map(float, time_str.replace(',', '.').split(':'))
    return h * 3600 + m * 60 + s

def total_time(intervals):
    seconds = 0
    for t, i in enumerate(intervals):
        duration = parse_time(i['to']) - parse_time(i['from'])
        print (f"Segment {t+1} duration: {round(duration, 2)} seconds (from {i['from']} to {i['to']})")
        seconds += duration
    print (f"Total duration for all segments: {round(seconds, 2)}")


def insert_silence(wav_file, intervals, output_file):
    with contextlib.closing(wave.open(wav_file, 'rb')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        channels = f.getnchannels()
        width = f.getsampwidth()
        audio_data = f.readframes(frames)
        audio = np.frombuffer(audio_data, dtype=np.int16).copy()  # create a mutable copy


    audio = audio.reshape(-1, channels)
    
    altaudio = []

    for interval in intervals:
        start = int((parse_time(interval['from'])-0.25) * rate)
        end = int((parse_time(interval['to'])+0.25) * rate)
        if len(altaudio) == 0:
            altaudio = audio[start:end]
        else:
            altaudio = np.append(altaudio, audio[start:end])
        
        audio[start:end] = 0  # Insert silence

    altaudio = altaudio.reshape(-1)
    audio = audio.reshape(-1)

    with contextlib.closing(wave.open('alt_audio.wav', 'wb')) as f:
        f.setnchannels(channels)
        f.setsampwidth(width)
        f.setframerate(rate)
        f.writeframes(altaudio.tobytes())


    with contextlib.closing(wave.open(output_file, 'wb')) as f:
        f.setnchannels(channels)
        f.setsampwidth(width)
        f.setframerate(rate)
        f.writeframes(audio.tobytes())


# Example usage
intervals = json.load(open('parsed_tempfile.wav.json'))
if len(intervals) == 0:
    print ("Error: no intervals found in input file")
    sys.exit(1)
wav_file = 'hq_tempfile.wav' 
output_file = 'cleaned_tempfile.wav'
total_time(intervals)
insert_silence(wav_file, intervals, output_file)

