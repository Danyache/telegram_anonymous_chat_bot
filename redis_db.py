import os
import logging
from typing import Set
import redis.asyncio as redis
from dotenv import load_dotenv

# Ensure environment variables are loaded (if not already done in the main file)
load_dotenv()

# Read redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
ACTIVE_USERS_KEY = "active_users"  # Redis key for storing active user ids

logger = logging.getLogger(__name__)

async def init_redis() -> redis.Redis:
    """
    Initialize and return an async Redis client.
    """
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    try:
        await redis_client.ping()
        logger.info("Connected to Redis successfully.")
    except Exception as e:
        logger.error("Failed to connect to Redis: %s", e)
        raise e
    return redis_client

async def add_user(redis_client: redis.Redis, user_id: int) -> None:
    """
    Add a user's chat ID to the Redis set for active users.
    
    Parameters:
        redis_client: The Redis client.
        user_id: The Telegram chat ID to add.
    """
    await redis_client.sadd(ACTIVE_USERS_KEY, user_id)
    logger.info("User %s added to Redis active users set.", user_id)

async def get_active_users(redis_client: redis.Redis) -> Set[int]:
    """
    Retrieve all active user IDs from Redis.
    
    Parameters:
        redis_client: The Redis client.
    
    Returns:
        A set of active user IDs (converted from bytes to ints).
    """
    user_ids = await redis_client.smembers(ACTIVE_USERS_KEY)
    # Convert returned bytes to integers
    active_users = {int(user_id) for user_id in user_ids}
    logger.info("Retrieved %d active users from Redis.", len(active_users))
    return active_users