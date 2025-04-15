# Anonymous Telegram Chat Bot

A Telegram bot that enables anonymous communication between users. 

## Features

- Users send messages to the bot
- Messages are forwarded anonymously to a channel
- Messages are broadcast to all other users of the bot
- Simple registration via /start command
- Support for forwarded messages with preserved attribution
- Photo sharing support

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
3. Create a `logs` directory for storing logs:
   ```
   mkdir -p logs
   ```
4. Run with Docker Compose:
   ```
   docker-compose up -d
   ```

   Or build and run with Docker directly:
   ```
   docker build -t telegram-anonymous-bot .
   docker run -d --restart always --name telegram-bot \
     -v $(pwd)/users.json:/app/users.json \
     -v $(pwd)/.env:/app/.env \
     -v $(pwd)/logs:/logs \
     telegram-anonymous-bot
   ```

## Usage

1. Start the bot by sending the `/start` command
2. Send any text message or photo to the bot:
   - It will be forwarded anonymously to the channel
   - It will be sent to all other users of the bot
3. Forward messages from other chats to the bot:
   - The forwarded message will be sent to the channel and other users with original attribution
   - Any caption you add will be sent as a separate anonymous message

## Logging and Monitoring

The bot uses a logging system that saves all activity to both the console and a persistent log file:

1. Logs are stored in the `./logs` directory on your host machine
2. The main log file is `./logs/bot.log`
3. To view real-time logs while the bot is running:
   ```
   docker-compose logs -f
   ```
4. Or check the log file directly:
   ```
   tail -f logs/bot.log
   ```

The logs contain information about:
- Bot startup and initialization
- Message handling (text, photos, forwards)
- User registrations
- Errors and exceptions

Logs are preserved between container restarts and system reboots.

## Troubleshooting

If messages aren't being sent to the channel:
1. Ensure the bot is an administrator in the channel
2. Try the `/testchannel` command to test the channel connection
3. Check the logs for any errors

## Project Structure

- `bot.py` - Main bot implementation with message handlers
- `utils.py` - Utility functions for message handling and user management
- `users.json` - Storage for registered users (created automatically)
- `.env` - Environment variables configuration
- `Dockerfile` and `docker-compose.yml` - Docker configuration
- `logs/` - Directory containing log files

## Requirements

- Python 3.7+
- aiogram 3.20.0
- python-dotenv 1.1.0
