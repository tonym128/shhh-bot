echo "Running FFMPEG"
ffmpeg -y -i /tmp/media -ar 16000 -ac 1 -c:a pcm_s16le /tmp/media.wav
echo "Running Whisper"
/usr/local/src/whisper $SHHH_WHISPER_OPTIONS -otxt -m /usr/local/src/models/ggml-model.bin /tmp/media.wav
echo "Complete"