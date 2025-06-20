# services/user_cache.py
import logging
from models.user_model import UserCreate
from logs.logging_config import setup_logger
from typing import Dict

logger = setup_logger()

TEMP_USER_CACHE: Dict[str, UserCreate] = {}

def cache_user_data(user: UserCreate):
    TEMP_USER_CACHE[user.username] = user
    logger.info(f"🕒 Cached raw data for user {user.username} for background sync.")

def pop_cached_user(username: str) -> UserCreate:
    return TEMP_USER_CACHE.pop(username, None)

def get_all_cached_users() -> Dict[str, UserCreate]:
    return TEMP_USER_CACHE
