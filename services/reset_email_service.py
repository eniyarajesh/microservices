from fastapi import HTTPException
from auth.keycloak_auth import get_admin_token, get_user_id
from utils.email_trigger import send_password_reset_email
import logging

logger = logging.getLogger(__name__)

# trigger email to reset password using SMTP
async def reset_password_email(username: str):
    try:
        token = await get_admin_token()
        user_id = await get_user_id(token, username)
        if not user_id:
            logger.error(f"User '{username}' not found in Keycloak")
            raise HTTPException(status_code=404, detail=f"User '{username}' not found in Keycloak")
        
        await send_password_reset_email(token, user_id)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.error(f"❌ Error in reset_password_email: {e}")
        raise HTTPException(status_code=500, detail="Failed to send reset password email")