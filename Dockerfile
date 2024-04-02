# Whisper Builder image
FROM python:3.9.13-alpine as builder

WORKDIR /usr/local/src
RUN apk update
RUN apk add git make g++ vim wget --upgrade bash
# whisper.cpp setup
RUN git clone https://github.com/ggerganov/whisper.cpp.git -b v1.5.4 --depth 1
WORKDIR /usr/local/src/whisper.cpp
RUN make 
RUN bash /usr/local/src/whisper.cpp/models/download-ggml-model.sh base

# Telegram Bot Image
FROM python:3.9.13-alpine
WORKDIR /usr/local/src/
RUN apk update
RUN apk add ffmpeg

# Copy whisper binary and model
COPY --from=builder /usr/local/src/whisper.cpp/main whisper
COPY --from=builder  /usr/local/src/whisper.cpp/models/ggml-base.bin ./models/ggml-base.bin

# Copy shhh.bot to the container
COPY shhh.py .
COPY convert.sh .
COPY requirements.txt .
RUN pip install -r requirements.txt
# Run bot when container starts
ENTRYPOINT [ "python", "shhh.py" ]
