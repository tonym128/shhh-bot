# Shhh Bot 
A Telegram Bot to convert speech to text from small videos and audio files.

This bot uses Docker, Telegram, Python and Whisper.cpp to stand up a small telegram bot on your own infrastructure which can take media and convert it to text.

The setup is meant to be as simple and quick as possible, so it's not meant for production use. It is intended for personal use only.

Tested on AMD64, provided build scripts for ARM64 and ARM32v7.

This was originally a Raspberry Pi 4 project I wrote and was manually running on a Pi. You can see a video about that here - https://www.youtube.com/watch?v=MjLzgebcDHo

And now it's a Docker container, which should be able to run on a Pi, Mac and Windows PC!

# Setup
## Create a Telegram Bot
- Create a new bot on Telegram and get the API key and chat ID for your bot.
    - Start a chat with @BotFather
    - Send /newbot to BotFather and follow the instructions to create a new bot
    - Copy the API key and chat ID for your bot
    - Get your chat ID by going to saved messages in Telegram and copying the number https://web.telegram.org/a/#12345678 in this example your chat id would be 12345678

## Change the model
The repository is currently configured to use the base model, but you can change it to any other supported model. 

In the Dockerfile, you only need to change this line

    ENV model="base"

"base" can be changed to any of the valid values accepted by whisper.cpp/models/download-ggml-model.sh

- Whisper models
    - tiny, tiny.en,tiny-q5_1, tiny.en-q5_1
    - base, base.en, base-q5_1, base.en-q5_1
    - small, small.en, small.en-tdrz, small-q5_1, small.en-q5_1
    - medium, medium.en, medium-q5_0, medium.en-q5_0
    - large-v1
    - large-v2, large-v2-q5_0
    - large-v3, large-v3-q5_0

## Docker Compose
    version: '3'

    services:
    shhhbot:
        container_name: shhhbot
        hostname: shhhbot
        restart: unless-stopped
        image: tmamacos/shhhbot:1.0
        environment:
        - SHHH_API_KEY={BOT_TOKEN}
        - SHHH_MY_CHAT_ID={YOUR_CHAT_ID}

## Build and run Docker image

    git clone https://github.com/tonym128/shhh-bot.git
    cd shhh-bot
    docker build -t shhhbot:1.0.
    docker run --env SHHH_API_KEY={BOT_TOKEN} --env SHHH_MY_CHAT_ID={YOUR_CHAT_ID} --name shhhbot -i shhhbot:1.0

Values should look something like this:
- SHHH_API_KEY=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
- SHHH_MY_CHAT_ID=12345678

## Build and push to DockerHub

    git clone https://github.com/tonym128/shhh-bot.git
    cd shhh-bot
    docker buildx create --name builder
    docker buildx use builder
    docker buildx inspect --bootstrap
    docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t {YOUR_USERNAME}/shhhbot:1.0 --push .
