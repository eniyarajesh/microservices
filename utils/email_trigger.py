import httpx
from fastapi import HTTPException
from config.settings import KEYCLOAK_REALM
import logging

logger = logging.getLogger(__name__)

# trigger email to reset password using SMTP
async def send_password_reset_email(token, user_id):
    url = f"http://localhost:8080/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/execute-actions-email"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = ["UPDATE_PASSWORD"]
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, headers=headers, json=payload)

        if response.status_code == 204:
            logger.info("✅ Password reset email sent.")
        else:
            logger.error(f"❌ Failed to send reset email. Status: {response.status_code}")
            logger.error(f"Response Text: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to send reset password email")
    except httpx.RequestError as e:
        logger.error(f"🔌 Connection error: {e}")
        raise HTTPException(status_code=503, detail="Keycloak server unreachable")
    except Exception as e:
        logger.error(f"❌ Unexpected error in send_password_reset_email: {e}")
        raise HTTPException(status_code=500, detail="Internal server error in sending reset email")





