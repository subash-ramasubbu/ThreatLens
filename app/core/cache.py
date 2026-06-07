import redis
import json
from app.core.config import settings

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

CACHE_TTL = 3600  # 1 hour in seconds


def get_cached(key: str):
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"Redis get error: {e}")
        return None


def set_cached(key: str, value: dict, ttl: int = CACHE_TTL):
    try:
        redis_client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        print(f"Redis set error: {e}")
        return False


def delete_cached(key: str):
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Redis delete error: {e}")
        return False


def clear_threats_cache():
    try:
        keys = redis_client.keys("threat:*")
        if keys:
            redis_client.delete(*keys)
        return True
    except Exception as e:
        print(f"Redis clear error: {e}")
        return False


def get_cache_stats():
    try:
        info = redis_client.info()
        keys = redis_client.dbsize()
        return {
            "total_keys": keys,
            "used_memory": info.get("used_memory_human", "unknown"),
            "hits": info.get("keyspace_hits", 0),
            "misses": info.get("keyspace_misses", 0),
            "uptime_seconds": info.get("uptime_in_seconds", 0),
        }
    except Exception as e:
        return {"error": str(e)}