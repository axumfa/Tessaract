import redis
import json
import logging

logging.basicConfig(level=logging.INFO)

# Try to connect to Redis, but make it optional for local development
cache = None
REDIS_AVAILABLE = False

try:
    cache = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=2)
    cache.ping()  # Test connection
    REDIS_AVAILABLE = True
    logging.info("Redis connection established. Caching enabled.")
except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
    REDIS_AVAILABLE = False
    cache = None
    # Only log once at startup, not on every request
    logging.warning("Redis not available. Cache will be disabled. Install and start Redis for caching functionality.")

def get_cached_transaction(transaction_id: str):
    if not REDIS_AVAILABLE or cache is None:
        return None
    try:
        result = cache.get(transaction_id)
        if result:
            logging.info(f"Cache hit for transaction {transaction_id}")
            return json.loads(result)
        logging.info(f"Cache miss for transaction {transaction_id}")
        return None
    except Exception as e:
        logging.error(f"Redis error: {str(e)}")
        return None

def cache_transaction(transaction_id: str, data: dict):
    if not REDIS_AVAILABLE or cache is None:
        return
    try:
        cache.set(transaction_id, json.dumps(data), ex=3600)
        logging.info(f"Cached transaction {transaction_id}")
    except Exception as e:
        logging.error(f"Failed to cache transaction {transaction_id}: {str(e)}")
