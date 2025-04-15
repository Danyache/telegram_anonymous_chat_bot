from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType, BotCommand, BotCommandScopeDefault
import asyncio
import logging
import os
from dotenv import load_dotenv
from utils import (
    send_to_channel, 
    broadcast_message, 
    load_users, 
    register_user,
    send_photo_to_channel,
    broadcast_photo,
    broadcast_forwarded_message,
    send_sticker_to_channel,
    broadcast_sticker,
    send_video_note_to_channel,
    broadcast_video_note
)


# Handler for the /start command:
async def start_handler(message: types.Message) -> None:
    """
    Handles the /start command:
    - Registers the user.
    - Sends a welcome message.
    """
    if message.from_user:
        user_id = message.from_user.id
        users = load_users()
        users = register_user(users, user_id)
        
        await message.answer(
            "👋 <b>Добро пожаловать в Анонимный Чат-бот!</b>\n\n"
            "Этот бот позволяет вам анонимно общаться с другими пользователями в канале \"Анонимное Завтра Вечером\".\n\n"
            "<b>Как он работает:</b>\n"
            "• Все сообщения, которые вы отправляете, анонимно пересылаются в канал\n"
            "• Эти сообщения также отправляются всем другим пользователям\n"
            "• Вы будете получать сообщения от других пользователей\n"
            "• Никто не будет знать, кто отправил какое сообщение\n\n"
            "<b>Ваша приватность защищена!</b> Начните отправлять сообщения прямо сейчас.",
            parse_mode="HTML"
        )
    else:
        await message.answer("Error: Could not identify user. Please try again.")

# Handler for the /testchannel command:
async def test_channel_handler(message: types.Message, bot: Bot) -> None:
    """
    Tests the connection to the channel without sending any messages.
    """
    if not message.from_user:
        await message.answer("Error: Could not identify user.")
        return
        
    await message.answer("Testing channel connection...")
    
    channel_id = os.getenv("CHANNEL_ID")
    if not channel_id:
        await message.answer("CHANNEL_ID not found in environment variables")
        return
        
    try:
        # Get current channel ID format
        await message.answer(f"Current channel ID: {channel_id}")
        
        # Try with direct channel ID
        try:
            direct_id = int(channel_id)
            # Just get chat info instead of sending a message
            chat = await bot.get_chat(chat_id=direct_id)
            await message.answer(f"✅ Channel connection successful\nChannel name: {chat.title}")
        except Exception as e:
            await message.answer(f"❌ Direct channel ID failed: {str(e)}")
            
        # Try with -100 prefix if needed
        if not str(channel_id).startswith('-100') and str(channel_id).startswith('-'):
            try:
                modified_id = int('-100' + str(channel_id)[1:])
                # Just get chat info instead of sending a message
                chat = await bot.get_chat(chat_id=modified_id)
                await message.answer(f"✅ Channel connection successful using modified ID: {modified_id}\nChannel name: {chat.title}")
            except Exception as e:
                await message.answer(f"❌ Modified channel ID failed: {str(e)}")
        
    except Exception as e:
        await message.answer(f"Channel test failed: {str(e)}")

# Handler for regular messages:
async def message_handler(message: types.Message, bot: Bot) -> None:
    """
    Handles incoming messages:
    - Ensures the user is registered.
    - Forwards the message to the channel.
    - Broadcasts the message to all active users (excluding the sender).
    """
    try:
        # Log the message content type
        content_type = message.content_type if hasattr(message, 'content_type') else "unknown"
        logging.info(f"Received message with content_type: {content_type}")
        
        # Check if it's a forwarded message
        is_forwarded = bool(message.forward_from or message.forward_from_chat)
        logging.info(f"Is forwarded message: {is_forwarded}")
        
        # Check message properties
        has_photo = bool(message.photo)
        has_text = bool(message.text)
        logging.info(f"Message properties - has_photo: {has_photo}, has_text: {has_text}")
        
        if not message.from_user:
            await message.answer("Error: Could not identify user. Please try again.")
            return
            
        user_id = message.from_user.id
        
        # Log user ID and message content
        log_message = ""
        if has_text and message.text:
            log_message = message.text[:200] + ("..." if len(message.text) > 200 else "")
        elif has_photo and message.caption:
            log_message = f"[PHOTO] " + (message.caption[:200] + ("..." if len(message.caption) > 200 else ""))
        elif has_photo:
            log_message = "[PHOTO WITHOUT CAPTION]"
        elif content_type == 'sticker':
            log_message = "[STICKER]"
        elif content_type == 'video_note':
            log_message = "[VIDEO NOTE]"
        elif is_forwarded:
            log_message = "[FORWARDED MESSAGE]"
        
        logging.info(f"Message from user {user_id}: {log_message}")
        
        users = load_users()
        users = register_user(users, user_id)
        
        channel_id = os.getenv("CHANNEL_ID")
        if not channel_id:
            logging.error("CHANNEL_ID not found in environment variables")
            return
        
        # Convert channel_id to int
        try:
            channel_id_int = int(channel_id)
        except ValueError:
            logging.error(f"Invalid channel ID: {channel_id}")
            return
        
        # Handle forwarded messages
        if is_forwarded:
            logging.info("Processing forwarded message")
            user_comment = ""
            comment_entities = None
            
            # If there's additional caption/text from the user, extract it
            if message.caption and not message.forward_from_chat:
                user_comment = message.caption
                comment_entities = message.caption_entities
                logging.info(f"Forwarded message has caption with {len(comment_entities) if comment_entities else 0} formatting entities")
            elif message.text and not message.forward_from_chat and content_type == 'text':
                # For text messages, we can't easily separate user comments from forwarded text
                # The whole text is considered part of the forwarded message
                pass
            
            # First, send the user's comment anonymously (if any)
            if user_comment:
                try:
                    logging.info(f"Sending user comment to channel: {user_comment}")
                    await send_to_channel(bot, channel_id_int, user_comment, entities=comment_entities)
                    await broadcast_message(bot, users, user_id, user_comment, entities=comment_entities)
                except Exception as e:
                    logging.error(f"Failed to send user comment: {e}")
            
            # Forward original message to channel with attribution preserved
            try:
                logging.info(f"Forwarding message to channel {channel_id_int}")
                await bot.forward_message(
                    chat_id=channel_id_int,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id
                )
            except Exception as e:
                logging.error(f"Failed to forward message to channel: {e}")
            
            # Broadcast to other users
            try:
                logging.info(f"Broadcasting forwarded message to other users")
                await broadcast_forwarded_message(
                    bot, 
                    users, 
                    user_id, 
                    message.chat.id, 
                    message.message_id
                )
            except Exception as e:
                logging.error(f"Failed to broadcast forwarded message: {e}")
            
            return
            
        # Handle photo messages - use content_type check as primary
        elif content_type == 'photo' or message.photo:
            logging.info("Processing photo message")
            # Check if photo is not empty
            if not message.photo:
                logging.error("Photo is empty despite content_type being 'photo'")
                return
                
            # Get the largest photo available (best quality)
            photo = message.photo[-1]
            photo_file_id = photo.file_id
            caption = message.caption or ""
            caption_entities = message.caption_entities  # Extract caption entities for formatting
            logging.info(f"Received photo from user {user_id} with file_id: {photo_file_id}, caption: {caption}")
            logging.info(f"Caption has {len(caption_entities) if caption_entities else 0} formatting entities")
            
            # Forward to channel
            try:
                logging.info(f"Sending photo to channel {channel_id_int}")
                await send_photo_to_channel(
                    bot, 
                    channel_id_int, 
                    photo_file_id, 
                    caption=caption,
                    caption_entities=caption_entities
                )
                logging.info("Photo sent to channel successfully")
            except Exception as e:
                logging.error(f"Failed to send photo to channel: {e}")
            
            # Broadcast to other users
            try:
                logging.info(f"Broadcasting photo to {len(users)} users")
                await broadcast_photo(
                    bot, 
                    users, 
                    user_id, 
                    photo_file_id, 
                    caption=caption,
                    caption_entities=caption_entities
                )
                logging.info("Photo broadcast to users successfully")
            except Exception as e:
                logging.error(f"Failed to broadcast photo: {e}")
            
            return
        
        # Handle text messages
        elif content_type == 'text' or message.text:
            logging.info("Processing text message")
            # Ensure text is not None
            if not message.text:
                logging.error("Text is empty despite content_type being 'text'")
                return
                
            text = message.text
            entities = message.entities  # Extract message entities for formatting
            logging.info(f"Message has {len(entities) if entities else 0} formatting entities")
            
            # Forward to channel
            try:
                logging.info(f"Forwarding message to channel {channel_id}")
                await send_to_channel(bot, channel_id_int, text, entities=entities)
            except Exception as e:
                logging.error(f"Failed to send message to channel: {e}")
            
            # Broadcast to other users
            await broadcast_message(bot, users, user_id, text, entities=entities)
            
            return
        
        # Handle sticker messages
        elif content_type == 'sticker' or message.sticker:
            logging.info("Processing sticker message")
            
            # Check if sticker is not empty
            if not message.sticker:
                logging.error("Sticker is empty despite content_type being 'sticker'")
                return
            
            # Get sticker file_id
            sticker_file_id = message.sticker.file_id
            logging.info(f"Received sticker from user {user_id} with file_id: {sticker_file_id}")
            
            # Forward to channel
            try:
                logging.info(f"Sending sticker to channel {channel_id_int}")
                await send_sticker_to_channel(bot, channel_id_int, sticker_file_id)
                logging.info("Sticker sent to channel successfully")
            except Exception as e:
                logging.error(f"Failed to send sticker to channel: {e}")
            
            # Broadcast to other users
            try:
                logging.info(f"Broadcasting sticker to {len(users)} users")
                await broadcast_sticker(bot, users, user_id, sticker_file_id)
                logging.info("Sticker broadcast to users successfully")
            except Exception as e:
                logging.error(f"Failed to broadcast sticker: {e}")
            
            return
        
        # Handle video notes (circle messages)
        elif content_type == 'video_note' or hasattr(message, 'video_note') and message.video_note:
            logging.info("Processing video note (circle message)")
            
            # Check if video note is not empty
            if not message.video_note:
                logging.error("Video note is empty despite content_type being 'video_note'")
                return
            
            # Get video note file_id
            video_note_file_id = message.video_note.file_id
            logging.info(f"Received video note from user {user_id} with file_id: {video_note_file_id}")
            
            # Forward to channel
            try:
                logging.info(f"Sending video note to channel {channel_id_int}")
                await send_video_note_to_channel(bot, channel_id_int, video_note_file_id)
                logging.info("Video note sent to channel successfully")
            except Exception as e:
                logging.error(f"Failed to send video note to channel: {e}")
            
            # Broadcast to other users
            try:
                logging.info(f"Broadcasting video note to {len(users)} users")
                await broadcast_video_note(bot, users, user_id, video_note_file_id)
                logging.info("Video note broadcast to users successfully")
            except Exception as e:
                logging.error(f"Failed to broadcast video note: {e}")
            
            return
        
        # Handle other message types (not supported)
        else:
            logging.info(f"Unsupported message type received: {content_type}")
            await message.answer("Sorry, I can only forward text, photos, stickers, video notes, and forwarded messages at this time.")
    
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        await message.answer("An error occurred while processing your message. Please try again later.")

# Set bot commands and description
async def set_bot_commands(bot: Bot) -> None:
    """
    Sets up the bot commands list that is shown in the bot interface.
    """
    commands = [
        BotCommand(command="start", description="Register with the bot and see welcome message"),
        BotCommand(command="testchannel", description="Test the connection to the channel (admin only)")
    ]
    
    await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
    logging.info("Bot commands have been set")

# Function to register all handlers with the Dispatcher:
def register_handlers(dp: Dispatcher, bot: Bot) -> None:
    """
    Registers the message handlers (start and message) with the Dispatcher.
    """
    # Register commands
    dp.message(Command("start"))(start_handler)
    
    # Fix: Create a wrapper function for testchannel that properly awaits
    @dp.message(Command("testchannel"))
    async def testchannel_wrapper(message: types.Message):
        await test_channel_handler(message, bot)
    
    # Fix: Create separate wrappers for different message types
    # This ensures message types are correctly identified
    @dp.message()
    async def message_wrapper(message: types.Message):
        logging.info(f"Received message in wrapper with content_type: {message.content_type}")
        await message_handler(message, bot)

# Main function as the entry point:
async def main() -> None:
    """
    - Loads environment variables.
    - Initializes logging.
    - Instantiates the Bot and Dispatcher.
    - Registers handlers.
    - Starts the polling loop.
    """
    # Load environment variables
    load_dotenv()
    
    # Ensure logs directory exists
    os.makedirs("/logs", exist_ok=True)
    
    # Configure logging to both console and file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Console handler
            logging.FileHandler("/logs/bot.log")  # File handler with absolute path
        ]
    )
    
    logging.info("Starting Telegram Anonymous Bot...")
    
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error("BOT_TOKEN not found in environment variables")
        return
    
    # Initialize bot and dispatcher with parse_mode to handle all message types
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    # Set bot commands
    await set_bot_commands(bot)
    
    # Register handlers
    register_handlers(dp, bot)
    
    # Start polling with allowed updates to ensure all message types are received
    logging.info("Bot is running. Press Ctrl+C to stop.")
    await dp.start_polling(bot, allowed_updates=["message", "edited_message", "channel_post", "edited_channel_post"])

if __name__ == "__main__":
    asyncio.run(main())
