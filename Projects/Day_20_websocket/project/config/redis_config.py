# config/redis_config.py

import redis
from redis.exceptions import RedisError
import os
from dotenv import load_dotenv


load_dotenv()


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Create Redis client
try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True,  # Return strings instead of bytes
        socket_connect_timeout=5,  # Timeout after 5s
        socket_timeout=5
    )
    
    # Test connection
    redis_client.ping()
    print("Redis connected successfully!")
    
except RedisError as e:
    print(f"Redis connection failed: {e}")
    print("Application will work without Redis (cache disabled)")
    redis_client = None


def get_redis_client():
    """Get Redis client instance"""
    return redis_client


def is_redis_available():
    """Check if Redis is available"""
    if redis_client is None:
        return False
    try:
        redis_client.ping()
        return True
    except RedisError:
        return False