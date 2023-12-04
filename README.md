# Remove Bad Words
Script that uses whisper.cpp to attempt to silence certain words in videos.

## Installation

1. Make sure you have a working copy of `whisper.cpp` installed, and that it works properly.
2. Make sure you have a recent version of `ffmpeg` installed.
3. Clone this repo somewhere: `git clone https://github.com/bsharper/remove_bad_words`
4. Enter the directory: `cd remove_bad_words`
5. Create a local python environment `python -m venv env`
6. Activate the local python environment `source env/bin/activate`
7. Install modules in requirements.txt `pip install -r requirements.txt`
8. Review `example_config.sh` and make any changes to point it to your local `whisper.cpp` binary and models. Save it as `config.sh`.
9. Run `./remove_bad_words.sh some_video_file.mp4` and wait for it to complete.

## Usage

1. Enable your local python environment: `source env/bin/activate`
2. Run `./remove_bad_words.sh some_file.mp4`
3. After generating a transcript, filtering it and producing a new audio track, a new video file will be generated under `CleanedUp_some_file.mp4`.

## (Optional) demucs music

1. This script can optionally work on music and isolate the vocal track.
2. This is enabled in `config.sh` by setting `IS_MUSIC=1`
3. To enable this, first make sure this project works on your local machine: https://github.com/xserrat/docker-facebook-demucs

## Troubleshooting

The python wrapper programs to show nice progress bars are mostly removable (`python run_ffmpeg.py` can be replaced with `ffmpeg`) to get more information if a step is failing.
