from models.user_model import UserCreate
from models.user_model import UserCreate
from config.settings import REDIS_HOST, REDIS_PORT
import logging
import redis
import json
import os


logger = logging.getLogger(__name__)


# REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
# REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

def cache_user_data(user: UserCreate):
    redis_client.set(user.username, json.dumps(user.dict()))
    logger.info(f"🕒 Cached raw data for user {user.username} for background sync.")

def pop_cached_user(username: str) -> UserCreate:
    raw_data = redis_client.get(username)
    if raw_data:
        redis_client.delete(username)
        return UserCreate(**json.loads(raw_data))
    return None

def get_all_cached_users() -> dict:
    cached_users = {}
    for key in redis_client.keys("*"):
        raw = redis_client.get(key)
        if raw:
            cached_users[key.decode()] = UserCreate(**json.loads(raw))
    return cached_users
