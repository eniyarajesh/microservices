import httpx
from fastapi import HTTPException
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
import logging

logger = logging.getLogger(__name__)

# get token to validate
async def get_access_token(username: str,password: str):
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT_ID,
        "client_secret": KEYCLOAK_CLIENT_SECRET,
        "username": username,
        "password": password,
        "scope": "openid"
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, data=data)

    if response.status_code != 200:
        try:
            detail_json = response.json()
            error_description = detail_json.get("error_description", "")
        except Exception:
            error_description = response.text

        # Log based on Keycloak's specific error
        if "account is not fully set up" in error_description.lower():
            logger.warning(f"🔒 User {username} must reset password before login (temporary password in effect)")
        else:
            logger.error(f"🚫 Invalid login for user {username}: {error_description}")

        raise HTTPException(status_code=401, detail=error_description)

    logger.info(f"Token is generated successfully for the user {username}")
    return response.json()





