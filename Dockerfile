# Whisper Builder image
FROM python:3.9.20-alpine as builder
# Model
# default to base
# Options as per download-ggml-model.sh - tiny.en tiny base.en base small.en small medium.en medium large-v1 large-v2 large-v3 large-v3-turbo
WORKDIR /usr/local/src
RUN set -e 
RUN apk update
RUN apk add ccache cmake build-base git make g++ vim wget --upgrade bash

# whisper.cpp setup
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.7.5 --depth 1
WORKDIR /usr/local/src/whisper.cpp
RUN make 

# Telegram Bot Image
FROM python:3.9.20-alpine
ARG model=tiny
LABEL org.opencontainers.image.title="Shhh-bot"
LABEL org.opencontainers.image.source=https://github.com/tonym128/shhh-bot
LABEL org.opencontainers.image.description=" A Telegram Bot to convert speech to text from small videos and audio files. "
WORKDIR /usr/local/src/
RUN apk update && apk add wget dos2unix --no-cache ffmpeg --upgrade bash

# Copy whisper binary and model downloader
COPY --from=builder /usr/local/src/whisper.cpp/build/bin/whisper-cli whisper
COPY --from=builder /usr/local/src/whisper.cpp/build/src/libwhisper* /usr/local/lib/
COPY --from=builder /usr/local/src/whisper.cpp/build/ggml/src/libggml* /usr/local/lib/
COPY --from=builder /usr/local/src/whisper.cpp/models/download-ggml-model.sh ./models/download-ggml-model.sh
COPY --from=builder /usr/local/src/whisper.cpp/models/download-ggml-model.sh /models/download-ggml-model.sh
RUN dos2unix ./models/download-ggml-model.sh
RUN dos2unix /models/download-ggml-model.sh
RUN /models/download-ggml-model.sh $model
RUN ln -s /models/ggml-$model.bin ./models/ggml-model.bin

# Install python requirements
COPY requirements.txt .
RUN /usr/local/bin/python -m pip install --upgrade pip && pip install -r requirements.txt

# Copy shhh.bot to the container
COPY shhh.py .

COPY convert.sh .
COPY download.sh .

RUN chmod +x *.sh
# Run bot when container starts
ENTRYPOINT [ "python", "shhh.py" ]
