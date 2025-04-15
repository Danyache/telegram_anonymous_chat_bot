from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import logging
import os
from dotenv import load_dotenv
from utils import send_to_channel, broadcast_message, load_users, register_user


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
    if not message.from_user:
        await message.answer("Error: Could not identify user. Please try again.")
        return
        
    user_id = message.from_user.id
    users = load_users()
    users = register_user(users, user_id)
    
    # Get the message text
    text = message.text or message.caption or ""
    if not text:
        await message.answer("Sorry, I can only forward text messages.")
        return
    
    # Forward to channel
    channel_id = os.getenv("CHANNEL_ID")
    if channel_id:
        try:
            logging.info(f"Forwarding message to channel {channel_id}")
            await send_to_channel(bot, int(channel_id), text)
        except Exception as e:
            logging.error(f"Failed to send message to channel: {e}")
            await message.answer("Your message was sent to other users, but failed to send to the channel. The admin has been notified.")
    else:
        logging.error("CHANNEL_ID not found in environment variables")
        await message.answer("Channel ID not configured. Please contact the bot administrator.")
    
    # Broadcast to other users
    await broadcast_message(bot, users, user_id, text)
    
    # Confirm to the sender
    await message.answer("Your message has been sent anonymously!")

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
    
    # Fix: Create a wrapper function for regular messages that properly awaits
    @dp.message()
    async def message_wrapper(message: types.Message):
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
    
    # Initialize bot and dispatcher
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    # Register handlers
    register_handlers(dp, bot)
    
    # Start polling
    logging.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
