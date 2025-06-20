import httpx
from fastapi import HTTPException, status
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
from logs.logging_config import setup_logger

logger = setup_logger()


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
        raise HTTPException(status_code=401, detail=response.text)
    return response.json()


async def validate_token_with_keycloak(token: str) -> dict:
    """
    Calls Keycloak's userinfo endpoint to validate token.
    """

    url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Keycloak response: {response.status_code} - {response.text}"
    )


