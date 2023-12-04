#!/bin/bash

WHISPER_MODEL_NAME=ggml-base.bin
WHISPER_PATH=~/projects/whisper.cpp

IS_MUSIC=1

# IS_MUSIC=1 will run demucs on the input file to create an isolated vocal track.
# This vocal track can either be used for transcription or when certain words are removed

USE_VOCALS_FOR_WHISPER=0

# USE_VOCALS_FOR_WHISPER=1 means only the isolated vocal track will be used for transcription
# otherwise it will only be used when silencing detected words

DEMUCS_DOCKER_PATH=~/projects/docker-facebook-demucs
# This is optional and only used if IS_MUSIC=1. This uses 
# the project here: https://github.com/xserrat/docker-facebook-demucs

BANNER_WIDTH=80

DEBUG=1
CLEANUP_FILES=1
EXIT_AFTER_DEBUG=0

export BANNER_WIDTH
export DEBUG
export CLEANUP_FILES
export DEMUCS_DOCKER_PATH
export EXIT_AFTER_DEBUG
export IS_MUSIC
export USE_VOCALS_FOR_WHISPER
export WHISPER_MODEL_NAME
export WHISPER_PATH
