#!/bin/bash

function usage {
	echo "Usage: ./$(basename $0) file_to_convert.mp4"
	echo ""
	echo ""
	exit 1
}

function cleanup {
	# skipping tempfile.wav.srt
	for a in tempfile.wav hq_tempfile.wav tempfile.wav.txt tempfile.wav.json parsed_tempfile.wav.json alt_audio.wav cleaned_tempfile.wav; do
    	if [[ -f "$a" ]]; then
			#echo "Removing temporary file $a"
			rm "$a"
		fi
	done
}

function check_path {
	if [[ -d "$1" ]] || [[ -f "$1" ]]; then
		echo -n "✅"
	else
		echo -n "❌"
	fi
}

if [[ ${#1} == 0 ]]; then
	usage
fi

if [[ ! -f "config.sh" ]]; then
	BANNER_WIDTH=60 python banner.py -c "Setup needed"
	echo "You need to set up a \"config.sh\" file for this script to work."
	echo "You should copy the \"example_config.sh\" to \"config.sh\" and modify it to fit your environment."
	echo ""
	usage
fi

. ./config.sh

WHISPER_BIN=$WHISPER_PATH/main
WHISPER_MODELS_PATH=$WHISPER_PATH/models
WHISPER_MODEL_PATH=$WHISPER_MODELS_PATH/$WHISPER_MODEL_NAME


DEMUCS_INPUT_PATH=$DEMUCS_DOCKER_PATH/input
DEMUCS_OUTPUT_PATH=$DEMUCS_DOCKER_PATH/output/htdemucs


if [[ $DEBUG == 1 ]]; then
	python banner.py -c "Debug info"
	echo "BANNER_WIDTH              : $BANNER_WIDTH"
	echo "WHISPER_MODEL_NAME        : $WHISPER_MODEL_NAME"
	echo "WHISPER_PATH              : $(check_path $WHISPER_PATH) $WHISPER_PATH"
	echo "WHISPER_BIN               : $(check_path $WHISPER_BIN) $WHISPER_BIN"
	echo "WHISPER_MODELS_PATH       : $(check_path $WHISPER_MODELS_PATH) $WHISPER_MODELS_PATH"
	echo "WHISPER_MODEL_PATH        : $(check_path $WHISPER_MODEL_PATH) $WHISPER_MODEL_PATH"
	echo "CLEANUP_FILES             : $CLEANUP_FILES"
	echo "IS_MUSIC                  : $IS_MUSIC"
	if [[ $IS_MUSIC == 1 ]]; then
		echo "USE_VOCALS_FOR_WHISEPER   : $USE_VOCALS_FOR_WHISPER"
		echo "DEMUCS_DOCKER_PATH        : $(check_path $DEMUCS_DOCKER_PATH) $DEMUCS_DOCKER_PATH"
		echo "DEMUCS_INPUT_PATH         : $(check_path $DEMUCS_INPUT_PATH) $DEMUCS_INPUT_PATH"
		echo "DEMUCS_OUTPUT_PATH        : $(check_path $DEMUCS_OUTPUT_PATH) $DEMUCS_OUTPUT_PATH"
	fi
	[[ $EXIT_AFTER_DEBUG == 1 ]] && exit
fi

python -c "import numpy; import alive_progress; import better_profanity" &>/dev/null
PYTHON_CHECK=$?

if [[ $PYTHON_CHECK != 0 ]]; then
	echo "Error: one of the Python libraries was not imported properly. Make sure to install requirements.txt (pip install -r requirements.txt)"
	exit 1
fi

if [[ ! -f "$WHISPER_BIN" ]] || [[ ! -f "$WHISPER_MODEL_PATH" ]]; then
	echo "whisper.cpp/main or whisper.cpp model not found"
	exit 1
fi

if [[ $IS_MUSIC == 1 ]] && [[ ! -d "$DEMUCS_DOCKER_PATH" ]]; then
	echo "Trying to demucs music but demucs path is invalid"
	exit 1
fi


INPUT_FILE="$1"
REAL_INPUT_FILE="$1"

set -e

# Convert music to constituent parts (if needed)

if [[ $IS_MUSIC == 1 ]]; then
	python banner.py -c "Converting for demucs"
	python run_ffmpeg.py -i "$INPUT_FILE" -y "$DEMUCS_INPUT_PATH/cleanmusic.mp3"
	python banner.py -c "Running demucs (may take a while)"
	CURRENT_PATH=$(pwd)
	cd "$DEMUCS_DOCKER_PATH"
	#make run track="cleanmusic.mp3" model=htdemucs gpu=false
	cd "$DEMUCS_OUTPUT_PATH/cleanmusic"
	ls
	cp *.wav "$CURRENT_PATH"
	cd "$CURRENT_PATH"
	if [[ $USE_VOCALS_FOR_WHISPER == 1 ]]; then
		INPUT_FILE="vocals.wav"
	fi
fi

# Convert 2 copies of input audio. One for whisper, one for later use when silencing
python banner.py -c "Converting input file for whisper"
python run_ffmpeg.py -i "$INPUT_FILE" -ar 16000 -ac 1 -c:a pcm_s16le "wh_tempfile.wav"
python run_ffmpeg.py -i "$INPUT_FILE" -c:a pcm_s16le "hq_tempfile.wav"
mv "wh_tempfile.wav" "tempfile.wav" # I forget why I did this...

# Generate transcript using whisper
python banner.py -c "Generating transcript"
python run_whisper.py "$WHISPER_BIN" "$WHISPER_MODEL_PATH" tempfile.wav

# Look for bad words
python banner.py -c "Scanning transcript"
python scan_transcript.py

# Handle vocal track 
if [[ $IS_MUSIC == 1 ]] && [[ $USE_VOCALS_FOR_WHISPER == 0 ]]; then
	python run_ffmpeg.py -i "$INPUT_FILE" -c:a pcm_s16le "hq_tempfile.wav"
fi

# Insert silence into wav file
python banner.py -c "Inserting silence into audio file"
python silencer.py

# Recombine audio if thats what we're doing 
if [[ $IS_MUSIC == 1 ]]; then
	python banner.py -c "Recombining vocal track with other tracks"
	mv cleaned_tempfile.wav cleaned_vocals.wav
	python run_ffmpeg.py -i drums.wav -i bass.wav -i other.wav -i cleaned_vocals.wav -filter_complex amix=inputs=4 -ac 1 cleaned_tempfile.wav
fi

# Making a new video file with original video but new audio
python banner.py -c "Creating new video file"
extension="${1##*.}"
#OUTPUT_FILENAME="cleaned_up_result.${extension}"
OUTPUT_FILENAME="CleanedUp_$1"
python run_ffmpeg.py -i "$1" -i cleaned_tempfile.wav -map 0:v -map 1:a -c:v copy -y "$OUTPUT_FILENAME"

python banner.py -c 'Done!'
echo ""
echo "File created \"$OUTPUT_FILENAME\" "
echo ""
if [[ $CLEANUP_FILES == 1 ]]; then
	cleanup
fi


