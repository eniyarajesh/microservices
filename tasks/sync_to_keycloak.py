from db.postgres import SessionLocal
from auth.keycloak_auth import keycloak_user_exists, sync_user_to_keycloak
from services.postgres_service import get_unsynced_users
from services.reset_email_service import reset_password_email
import logging

logger = logging.getLogger(__name__)


async def sync_unsynced_users():
    db = SessionLocal()
    users = get_unsynced_users(db)

    if not users:
        logger.info(f"No users to sync")

    for user in users:
        try: 
            logger.info(f"🔁 Syncing {user.username} to Keycloak")
            if await keycloak_user_exists(user.username):
                logger.warning(f"🔁 Skipping {user.username}: already exists in Keycloak")
                user.synced = True    # Optional: Mark as synced to stop retrying
                db.commit()
                continue

            await sync_user_to_keycloak(user)  # This should create the user in Keycloak
            user.synced = True
            db.commit()
            logger.info(f"✅ Synced {user.username} to Keycloak")

            await reset_password_email(user.username)

        except Exception as e:
            logger.error(f"❌ Failed to sync {user.username}: {e}")

    db.close()



