echo "Running FFMPEG"
ffmpeg -y -i $0 -ar 16000 -ac 1 -c:a pcm_s16le $0.wav
echo "Running Whisper"
/usr/local/src/whisper $SHHH_WHISPER_OPTIONS -otxt -m /usr/local/src/models/ggml-model.bin $0.wav
echo "Complete"