# Anonymous Telegram Chat Bot

A Telegram bot that enables anonymous communication between users. 

## Features

- Users send messages to the bot
- Messages are forwarded anonymously to a channel
- Messages are broadcast to all other users of the bot
- Simple registration via /start command

## Setup

### Option 1: Standard Setup

1. Clone this repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   BOT_TOKEN=your_bot_token
   CHANNEL_ID=your_channel_id
   ```
   - `BOT_TOKEN`: Get this by creating a bot through the [BotFather](https://t.me/botfather)
   - `CHANNEL_ID`: The ID of your Telegram channel (the bot must be an admin of this channel)

4. Run the bot:
   ```
   python bot.py
   ```

### Option 2: Docker Setup

1. Clone this repository
2. Create a `.env` file with your bot token and channel ID (as shown above)
3. Run with Docker Compose:
   ```
   docker-compose up -d
   ```

   Or build and run with Docker directly:
   ```
   docker build -t telegram-anonymous-bot .
   docker run -d --restart always --name telegram-bot -v $(pwd)/users.json:/app/users.json -v $(pwd)/.env:/app/.env telegram-anonymous-bot
   ```

## Usage

1. Start the bot by sending the `/start` command
2. Send any text message to the bot:
   - It will be forwarded anonymously to the channel
   - It will be sent to all other users of the bot
3. All messages from other users will be received by you
