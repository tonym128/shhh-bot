# Shhh Bot 
A Telegram Bot to convert speech to text from small videos and audio files.

This bot uses Docker, Telegram, Python and Whisper.cpp to stand up a small telegram bot on your own infrastructure which can take media and convert it to text.

The setup is meant to be as simple and quick as possible, so it's not meant for production use. It is intended for personal use only.

Tested on AMD64, provided build scripts for ARM64 and ARM32v7.

This was originally a Raspberry Pi 4 project I wrote and was manually running on a Pi. You can see a video about that here - https://www.youtube.com/watch?v=MjLzgebcDHo

And now it's a Docker container, which can run on a Pi, Mac and Windows PC!

# Setup
## Create a Telegram Bot
- Create a new bot on Telegram and get the API key and chat ID for your bot.
    - Start a chat with @BotFather
    - Send /newbot to BotFather and follow the instructions to create a new bot
    - Copy the API key and chat ID for your bot
    - Get your chat ID by going to saved messages in Telegram and copying the number https://web.telegram.org/a/#12345678 in this example your chat id would be 12345678

## Change the model
See the Docker Compose Environment SHHH_WHISPER_MODEL to have your desired model downloaded to /models at startup, which can be persisted across Shhh-bot versions.

The Dockerfile in the repository is currently configured to use the base model, but you can change it to any other supported model. 

In the Dockerfile, you only need to change this line

    ARG model="base"

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
        image: ghcr.io/tonym128/shhh-bot
        environment:
        - SHHH_API_KEY={BOT_TOKEN}
        # Optional
        # - SHHH_MY_CHAT_ID={YOUR_CHAT_ID} 
        # - SHHH_ALLOWED_CHAT_IDS={YOUR_CHAT_ID ANOTHER_CHAT_ID ANOTHER_CHAT_ID}
        # - SHHH_WHISPER_MODEL=medium 
        # - SHHH_WHISPER_OPTIONS=-l nl
    volumes:
      - models:/models
volumes:
  models:

### Environment Options
#### SHHH_API_KEY={BOT_TOKEN}

This is the only required Environment variable and it is the Bot Token your Bot will operate under. See Setup - Create a Telegram Bot at the top for how to provision this.

#### SHHH_MY_CHAT_ID={YOUR_CHAT_ID}

Supply a chat_id here to receive all admin messages, messages will go to docker logs, but this would provide more instant access to processing happening on your bot.

#### SHHH_ALLOWED_CHAT_IDS={YOUR_CHAT_ID ANOTHER_CHAT_ID ANOTHER_CHAT_ID}

If you wish for only certain people to use the bot, you can specify their chat_id's here, you can also add groups, which are negative numbers, if you wish for a group to be able to use the bot.

#### SHHH_WHISPER_MODEL=medium 

You can specify any model Whisper supports and it will be downloaded for you on startup and stored in /models, which you can mount for persistence.

#### SHHH_WHISPER_OPTIONS=-l nl

You can provide any additional Whisper command line options you want. For instance, -l specifies the language you're speaking in, by default it is set to en for English and will output response in English, potentially even translating whatever speech it detects into English.
nl specifies dutch in this case and the text will be output in Dutch.

### Volume mount

The volume mount provides a place to store the models seperately from the container.

A few prebuilt images with a model supplied
- ghcr.io/tonym128/shhh-bot
- ghcr.io/tonym128/shhh-bot-base
- ghcr.io/tonym128/shhh-bot-small

Shhh-bot includes the tiny model, base and small include those models
When a model is selected via the SHHH_WHISPER_MODEL it can be any of the default models supported by Whispers built in download functionality.
The model is stored in /model and you can avoid having to download it multiple times using the persistence of a docker volume. Try out other models and switch back and forth between them, as long as you have the volume, you won't have to download it again.

## Build and run Docker image

    git clone https://github.com/tonym128/shhh-bot.git
    cd shhh-bot
    docker build -t shhh-bot:1.0 .
    docker run --env SHHH_API_KEY={BOT_TOKEN} --env SHHH_MY_CHAT_ID={YOUR_CHAT_ID} --name shhhbot -i shhh-bot:1.0

Values should look something like this:
- SHHH_API_KEY=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

The following two are optional:
Admin chat id for receiving messages:
    - SHHH_MY_CHAT_ID=12345678
Space seperated list of chat id's that are allowed to talk to your service:
    - SHHH_ALLOWED_CHAT_IDS={YOUR_CHAT_ID ANOTHER_CHAT_ID ANOTHER_CHAT_ID}

### Export built image to tar and upload directly to your server
- ```docker save shhhbot:1.0 > shhhbot.tar```
- Import image in Portainer by going to images and importing a new image from a tar file and upload with a name and tag eg shhhbot:1.0

## Build and push to DockerHub

    git clone https://github.com/tonym128/shhh-bot.git
    cd shhh-bot
    docker buildx create --name builder
    docker buildx use builder
    docker buildx inspect --bootstrap
    docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 -t {YOUR_USERNAME}/shhhbot:1.0 --push .
