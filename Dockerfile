# Whisper Builder image
FROM python:3.9.13-alpine as builder
# Model
# default to base
# Options as per download-ggml-model.sh eg tiny, base, large-v1, large-v2, large-v2, 
WORKDIR /usr/local/src
RUN apk update
RUN apk add git make g++ vim wget --upgrade bash
# whisper.cpp setup
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.5.4 --depth 1
WORKDIR /usr/local/src/whisper.cpp
RUN make 

# Telegram Bot Image
FROM python:3.9.13-alpine
ARG model=tiny
LABEL org.opencontainers.image.title="Shhh-bot"
LABEL org.opencontainers.image.source=https://github.com/tonym128/shhh-bot
LABEL org.opencontainers.image.description=" A Telegram Bot to convert speech to text from small videos and audio files. "
WORKDIR /usr/local/src/
RUN apk update && apk add wget dos2unix --no-cache ffmpeg --upgrade bash

# Copy whisper binary and model downloader
COPY --from=builder /usr/local/src/whisper.cpp/main whisper
COPY --from=builder /usr/local/src/whisper.cpp/models/download-ggml-model.sh ./models/download-ggml-model.sh
COPY --from=builder /usr/local/src/whisper.cpp/models/download-ggml-model.sh /models/download-ggml-model.sh
RUN dos2unix ./models/download-ggml-model.sh
RUN dos2unix /models/download-ggml-model.sh
RUN /models/download-ggml-model.sh $model
RUN ln -s /models/ggml-$model.bin ./models/ggml-model.bin

# Copy shhh.bot to the container
COPY shhh.py .
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY convert.sh .
COPY download.sh .

# Run bot when container starts
ENTRYPOINT [ "python", "shhh.py" ]
