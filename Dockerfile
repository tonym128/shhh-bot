# Model
# Options as per download-ggml-model.sh eg tiny, base, large-v1, large-v2, large-v2

# Whisper Builder image
FROM python:3.9.13-alpine as builder
ENV model="base"
WORKDIR /usr/local/src
RUN apk update
RUN apk add git make g++ vim wget --upgrade bash
# whisper.cpp setup
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.5.4 --depth 1
WORKDIR /usr/local/src/whisper.cpp
RUN make 
RUN /usr/local/src/whisper.cpp/models/download-ggml-model.sh $model
RUN mv ./models/ggml-$model.bin ./models/ggml-model.bin

# Whisper Image
FROM python:3.9.13-alpine as whisper
WORKDIR /usr/local

# Telegram Bot Image
FROM python:3.9.13-alpine
LABEL org.opencontainers.image.description  A Telegram Bot to convert speech to text from small videos and audio files. 
WORKDIR /usr/local/src/
RUN apk update && apk add --no-cache ffmpeg

# Copy whisper binary and model
COPY --from=builder /usr/local/src/whisper.cpp/main whisper
COPY --from=builder  /usr/local/src/whisper.cpp/models/ggml-model.bin ./models/ggml-model.bin

# Copy shhh.bot to the container
COPY shhh.py .
COPY convert.sh .
COPY requirements.txt .
RUN pip install -r requirements.txt
# Run bot when container starts
ENTRYPOINT [ "python", "shhh.py" ]
