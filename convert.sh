ffmpeg -y -i $1 -ar 16000 -ac 1 -c:a pcm_s16le $1.wav
/usr/local/src/whisper -otxt -m /usr/local/src/models/ggml-base.bin $1.wav
