from aiogram import Bot
from typing import Set, List, Optional, Union
import os
import json
import logging
from io import BytesIO
import traceback


# Function to forward a message to a specific channel:
async def send_to_channel(bot: Bot, channel_id: int, message_text: str, entities=None) -> None:
    """
    Sends the message text to the designated Telegram channel using the provided bot.
    
    Parameters:
      bot: The Telegram Bot instance.
      channel_id: The target channel's numeric ID.
      message_text: The text of the message to send.
      entities: Optional message entities to preserve formatting.
    """
    try:
        # Ensure channel_id is properly formatted
        channel_id_str = str(channel_id)
        # If it doesn't start with '-100', add it (for supergroups and channels)
        if not channel_id_str.startswith('-100') and channel_id_str.startswith('-'):
            # Strip the leading minus and add -100
            channel_id_str = '-100' + channel_id_str[1:]
            channel_id = int(channel_id_str)
            
        logging.info(f"Attempting to send message to channel: {channel_id}")
        await bot.send_message(
            chat_id=channel_id, 
            text=message_text,
            entities=entities  # Pass entities to preserve formatting
        )
        logging.info("Message sent to channel successfully")
    except Exception as e:
        logging.error(f"Error sending message to channel {channel_id}: {e}")
        # Print detailed error for debugging
        traceback.print_exc()

# Function to send image to the channel
async def send_photo_to_channel(bot: Bot, channel_id: int, photo_file_id: str, caption: Optional[str] = None, caption_entities=None) -> None:
    """
    Sends a photo to the designated Telegram channel using the provided bot.
    
    Parameters:
      bot: The Telegram Bot instance.
      channel_id: The target channel's numeric ID.
      photo_file_id: The file_id of the photo to send.
      caption: Optional caption for the photo.
      caption_entities: Optional caption entities to preserve formatting.
    """
    try:
        # Ensure channel_id is properly formatted
        channel_id_str = str(channel_id)
        if not channel_id_str.startswith('-100') and channel_id_str.startswith('-'):
            channel_id_str = '-100' + channel_id_str[1:]
            channel_id = int(channel_id_str)
            
        logging.info(f"Attempting to send photo to channel: {channel_id}")
        await bot.send_photo(
            chat_id=channel_id, 
            photo=photo_file_id, 
            caption=caption,
            caption_entities=caption_entities
        )
        logging.info("Photo sent to channel successfully")
    except Exception as e:
        logging.error(f"Error sending photo to channel {channel_id}: {e}")
        traceback.print_exc()

# Function to broadcast a message to active users (excluding the sender):
async def broadcast_message(
    bot: Bot,
    active_users: List[int],
    exclude_user_id: int,
    message_text: str,
    entities=None
) -> None:
    """
    Broadcasts the message to all active users except the sender.
    
    Parameters:
      bot: The Telegram Bot instance.
      active_users: A list of user chat IDs to send the message to.
      exclude_user_id: The sender's ID to be excluded from broadcasting.
      message_text: The text of the message to broadcast.
      entities: Optional message entities to preserve formatting.
    """
    for user_id in active_users:
        if user_id != exclude_user_id:
            try:
                await bot.send_message(
                    chat_id=user_id, 
                    text=message_text,
                    entities=entities  # Pass entities to preserve formatting
                )
            except Exception as e:
                logging.error(f"Error sending message to user {user_id}: {e}")

# Function to broadcast a photo to active users
async def broadcast_photo(
    bot: Bot,
    active_users: List[int],
    exclude_user_id: int,
    photo_file_id: str,
    caption: Optional[str] = None,
    caption_entities=None
) -> None:
    """
    Broadcasts a photo to all active users except the sender.
    
    Parameters:
      bot: The Telegram Bot instance.
      active_users: A list of user chat IDs to send the message to.
      exclude_user_id: The sender's ID to be excluded from broadcasting.
      photo_file_id: The file_id of the photo to send.
      caption: Optional caption for the photo.
      caption_entities: Optional caption entities to preserve formatting.
    """
    for user_id in active_users:
        if user_id != exclude_user_id:
            try:
                await bot.send_photo(
                    chat_id=user_id, 
                    photo=photo_file_id, 
                    caption=caption,
                    caption_entities=caption_entities
                )
            except Exception as e:
                logging.error(f"Error sending photo to user {user_id}: {e}")

# Function to broadcast a forwarded message to users
async def broadcast_forwarded_message(
    bot: Bot,
    active_users: List[int],
    exclude_user_id: int,
    from_chat_id: int,
    message_id: int
) -> None:
    """
    Broadcasts a forwarded message to all active users except the sender.
    
    Parameters:
      bot: The Telegram Bot instance.
      active_users: A list of user chat IDs to send the message to.
      exclude_user_id: The sender's ID to be excluded from broadcasting.
      from_chat_id: The original chat ID containing the message.
      message_id: The ID of the message to forward.
    """
    for user_id in active_users:
        if user_id != exclude_user_id:
            try:
                # Use forward_message to preserve the forwarded status
                await bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=from_chat_id,
                    message_id=message_id
                )
            except Exception as e:
                logging.error(f"Error forwarding message to user {user_id}: {e}")

# Functions to manage users storage:
def load_users() -> List[int]:
    """
    Loads the list of active user IDs from the storage file.
    
    Returns:
      A list of user IDs.
    """
    try:
        if os.path.exists("users.json"):
            with open("users.json", "r") as file:
                return json.load(file)
        return []
    except Exception as e:
        logging.error(f"Error loading users: {e}")
        return []

def save_users(users: List[int]) -> None:
    """
    Saves the list of active users to the storage file.
    
    Parameters:
      users: The list of user IDs to save.
    """
    try:
        with open("users.json", "w") as file:
            json.dump(users, file)
    except Exception as e:
        logging.error(f"Error saving users: {e}")

def register_user(users: List[int], user_id: int) -> List[int]:
    """
    Adds a user's chat ID to the active users list if not already present.
    
    Parameters:
      users: The list containing active user IDs.
      user_id: The chat ID of the user to register.
      
    Returns:
      The updated list of users.
    """
    if user_id not in users:
        users.append(user_id)
        save_users(users)
        logging.info(f"New user registered: {user_id}")
    return users

# Function to send a sticker to the channel
async def send_sticker_to_channel(bot: Bot, channel_id: int, sticker_file_id: str) -> None:
    """
    Sends a sticker to the designated Telegram channel using the provided bot.
    
    Parameters:
      bot: The Telegram Bot instance.
      channel_id: The target channel's numeric ID.
      sticker_file_id: The file_id of the sticker to send.
    """
    try:
        # Ensure channel_id is properly formatted
        channel_id_str = str(channel_id)
        if not channel_id_str.startswith('-100') and channel_id_str.startswith('-'):
            channel_id_str = '-100' + channel_id_str[1:]
            channel_id = int(channel_id_str)
            
        logging.info(f"Attempting to send sticker to channel: {channel_id}")
        await bot.send_sticker(chat_id=channel_id, sticker=sticker_file_id)
        logging.info("Sticker sent to channel successfully")
    except Exception as e:
        logging.error(f"Error sending sticker to channel {channel_id}: {e}")
        traceback.print_exc()

# Function to broadcast a sticker to active users
async def broadcast_sticker(
    bot: Bot,
    active_users: List[int],
    exclude_user_id: int,
    sticker_file_id: str
) -> None:
    """
    Broadcasts a sticker to all active users except the sender.
    
    Parameters:
      bot: The Telegram Bot instance.
      active_users: A list of user chat IDs to send the message to.
      exclude_user_id: The sender's ID to be excluded from broadcasting.
      sticker_file_id: The file_id of the sticker to send.
    """
    for user_id in active_users:
        if user_id != exclude_user_id:
            try:
                await bot.send_sticker(chat_id=user_id, sticker=sticker_file_id)
            except Exception as e:
                logging.error(f"Error sending sticker to user {user_id}: {e}")

# Function to send a video note to the channel
async def send_video_note_to_channel(bot: Bot, channel_id: int, video_note_file_id: str) -> None:
    """
    Sends a video note (circle message) to the designated Telegram channel using the provided bot.
    
    Parameters:
      bot: The Telegram Bot instance.
      channel_id: The target channel's numeric ID.
      video_note_file_id: The file_id of the video note to send.
    """
    try:
        # Ensure channel_id is properly formatted
        channel_id_str = str(channel_id)
        if not channel_id_str.startswith('-100') and channel_id_str.startswith('-'):
            channel_id_str = '-100' + channel_id_str[1:]
            channel_id = int(channel_id_str)
            
        logging.info(f"Attempting to send video note to channel: {channel_id}")
        await bot.send_video_note(chat_id=channel_id, video_note=video_note_file_id)
        logging.info("Video note sent to channel successfully")
    except Exception as e:
        logging.error(f"Error sending video note to channel {channel_id}: {e}")
        traceback.print_exc()

# Function to broadcast a video note to active users
async def broadcast_video_note(
    bot: Bot,
    active_users: List[int],
    exclude_user_id: int,
    video_note_file_id: str
) -> None:
    """
    Broadcasts a video note (circle message) to all active users except the sender.
    
    Parameters:
      bot: The Telegram Bot instance.
      active_users: A list of user chat IDs to send the message to.
      exclude_user_id: The sender's ID to be excluded from broadcasting.
      video_note_file_id: The file_id of the video note to send.
    """
    for user_id in active_users:
        if user_id != exclude_user_id:
            try:
                await bot.send_video_note(chat_id=user_id, video_note=video_note_file_id)
            except Exception as e:
                logging.error(f"Error sending video note to user {user_id}: {e}")
