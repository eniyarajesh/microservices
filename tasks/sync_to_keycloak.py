from auth.keycloak_auth import create_keycloak_user
from redis_cache.user_cache import get_all_cached_users, pop_cached_user
import logging

logger = logging.getLogger(__name__)


# sync user to keycloak (background task)
async def sync_users_to_keycloak():
    cached_users = get_all_cached_users()

    if not cached_users:
        logger.info("No cached users to sync.")
        return

    for username, user_data in list(cached_users.items()):
        logger.info(f"🔄 Syncing {username} to Keycloak")
        try:
            await create_keycloak_user(user_data)
            pop_cached_user(username)
            logger.info(f"✅ Synced {username} to Keycloak")
        except Exception as e:
            logger.error(f"❌ Failed to sync {username}: {str(e)}")

