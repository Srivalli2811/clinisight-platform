import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

def get_from_cache(key: str):
    """Returns cached Python object or None if miss/expired."""
    cached = redis_client.get(key)

    if cached is not None:
        return json.loads(cached)

    return None

def set_in_cache(key: str, value, expiry_seconds: int = 60):
    """Stores value in Redis with expiry. Value must be JSON-serializable."""
    redis_client.setex(key, expiry_seconds, json.dumps(value))

def delete_from_cache(key: str):
    """Removes a key from Redis immediately — used for cache invalidation."""
    redis_client.delete(key)


def is_redis_available():
    """Returns True if Redis is reachable."""
    try:
        redis_client.ping()
        return True
    except Exception:
        return False