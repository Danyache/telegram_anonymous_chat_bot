from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ContentType
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
    broadcast_photo
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
            "Welcome to the Anonymous Chat Bot!\n"
            "Any message you send here will be forwarded anonymously to the channel "
            "and to all other users of this bot."
        )
    else:
        await message.answer("Error: Could not identify user. Please try again.")

# Handler for the /testchannel command:
async def test_channel_handler(message: types.Message, bot: Bot) -> None:
    """
    Tests the connection to the channel by sending a test message.
    """
    if not message.from_user:
        await message.answer("Error: Could not identify user.")
        return
        
    # Only allow admins to run this command
    # In a real bot, you'd check if the user is an admin
    
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
            await bot.send_message(chat_id=direct_id, text="Test message (direct ID)")
            await message.answer("✅ Direct channel ID works")
        except Exception as e:
            await message.answer(f"❌ Direct channel ID failed: {str(e)}")
            
        # Try with -100 prefix if needed
        if not str(channel_id).startswith('-100') and str(channel_id).startswith('-'):
            try:
                modified_id = int('-100' + str(channel_id)[1:])
                await bot.send_message(chat_id=modified_id, text="Test message (modified ID)")
                await message.answer(f"✅ Modified channel ID works: {modified_id}")
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
        
        # Check message properties
        has_photo = bool(message.photo)
        has_text = bool(message.text)
        logging.info(f"Message properties - has_photo: {has_photo}, has_text: {has_text}")
        
        if not message.from_user:
            await message.answer("Error: Could not identify user. Please try again.")
            return
            
        user_id = message.from_user.id
        users = load_users()
        users = register_user(users, user_id)
        
        channel_id = os.getenv("CHANNEL_ID")
        if not channel_id:
            logging.error("CHANNEL_ID not found in environment variables")
            await message.answer("Channel ID not configured. Please contact the bot administrator.")
            return
        
        # Convert channel_id to int
        try:
            channel_id_int = int(channel_id)
        except ValueError:
            logging.error(f"Invalid channel ID: {channel_id}")
            await message.answer("Invalid channel ID. Please contact the bot administrator.")
            return
        
        # Handle photo messages - use content_type check as primary
        if content_type == 'photo' or message.photo:
            logging.info("Processing photo message")
            # Check if photo is not empty
            if not message.photo:
                logging.error("Photo is empty despite content_type being 'photo'")
                await message.answer("Error processing your photo. Please try again.")
                return
                
            # Get the largest photo available (best quality)
            photo = message.photo[-1]
            photo_file_id = photo.file_id
            caption = message.caption or ""
            
            logging.info(f"Received photo from user {user_id} with file_id: {photo_file_id}, caption: {caption}")
            
            # Forward to channel
            try:
                logging.info(f"Sending photo to channel {channel_id_int}")
                await send_photo_to_channel(bot, channel_id_int, photo_file_id, caption)
                logging.info("Photo sent to channel successfully")
            except Exception as e:
                logging.error(f"Failed to send photo to channel: {e}")
                await message.answer("Your photo was sent to other users, but failed to send to the channel.")
            
            # Broadcast to other users
            try:
                logging.info(f"Broadcasting photo to {len(users)} users")
                await broadcast_photo(bot, users, user_id, photo_file_id, caption)
                logging.info("Photo broadcast to users successfully")
            except Exception as e:
                logging.error(f"Failed to broadcast photo: {e}")
            
            # Confirm to the sender
            await message.answer("Your photo has been sent anonymously!")
            return
        
        # Handle text messages
        elif content_type == 'text' or message.text:
            logging.info("Processing text message")
            # Ensure text is not None
            if not message.text:
                logging.error("Text is empty despite content_type being 'text'")
                await message.answer("Error processing your message. Please try again.")
                return
                
            text = message.text
            
            # Forward to channel
            try:
                logging.info(f"Forwarding message to channel {channel_id}")
                await send_to_channel(bot, channel_id_int, text)
            except Exception as e:
                logging.error(f"Failed to send message to channel: {e}")
                await message.answer("Your message was sent to other users, but failed to send to the channel. The admin has been notified.")
            
            # Broadcast to other users
            await broadcast_message(bot, users, user_id, text)
            
            # Confirm to the sender
            await message.answer("Your message has been sent anonymously!")
            return
        
        # Handle other message types (not supported)
        else:
            logging.info(f"Unsupported message type received: {content_type}")
            await message.answer("Sorry, I can only forward text and photos at this time.")
    
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        import traceback
        traceback.print_exc()
        await message.answer("An error occurred while processing your message. Please try again later.")

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
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Get bot token from environment
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        logging.error("BOT_TOKEN not found in environment variables")
        return
    
    # Initialize bot and dispatcher with parse_mode to handle all message types
    bot = Bot(token=bot_token, parse_mode=None)
    dp = Dispatcher()
    
    # Register handlers
    register_handlers(dp, bot)
    
    # Start polling with allowed updates to ensure all message types are received
    logging.info("Starting bot...")
    await dp.start_polling(bot, allowed_updates=["message", "edited_message", "channel_post", "edited_channel_post"])

if __name__ == "__main__":
    asyncio.run(main())
