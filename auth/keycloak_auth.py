import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user_model import UserCreate
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM
from db.postgres import SessionLocal
from services.user_service import mark_user_as_synced
import logging 
import httpx

token_scheme = HTTPBearer()

logger = logging.getLogger(__name__)

# validate the given user with the access_token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_scheme)):
    token = credentials.credentials

    url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)

        logger.info(f"[Keycloak] /userinfo status: {response.status_code}")
        logger.debug(f"[Keycloak] /userinfo response: {response.text}")

        if response.status_code != 200:
            logger.error(f"Unauthorized: Token invalid or expired. {response.text}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Unauthorized: Token invalid or expired. {response.text}"
            )

        user_info = response.json()

        # Optional sanity check: ensure essential fields are present
        if "preferred_username" not in user_info:
            logger.error(f"Invalid token payload: missing 'preferred_username'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload: missing 'preferred_username'"
            )

        logger.info(f"✅ Authorized user: {user_info['preferred_username']}")
        return user_info

    except httpx.RequestError as e:
        logger.error(f"🔌 Connection error with Keycloak: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Keycloak unavailable. Try again later."
        )
    except Exception as e:
        logger.error(f"❌ Unexpected error in auth: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during token validation."
        )


# get admin token
async def get_admin_token():
    async with httpx.AsyncClient() as client:
        url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": os.getenv("KEYCLOAK_ADMIN", "admin"),
            "password": os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin")
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=data)
            if response.status_code != 200:
                logger.error(f"Keycloak auth failed: {response.text}")
                raise HTTPException(status_code=500, detail=response.text)
            return response.json()["access_token"]


# check user already exist in keycloak
async def keycloak_user_exists(username: str) -> bool:
    token = await get_admin_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={username}"
        response = await client.get(url, headers=headers)
        return bool(response.json())


# store user data in keycloak 
async def create_keycloak_user(user_data: UserCreate):
    token = await get_admin_token()       # get token from admin to add user in keycloak
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "username": user_data.username,
        "email": user_data.email,
        "enabled": True,
        "emailVerified": True,
        "firstName": user_data.firstName,
        "lastName": user_data.lastName,
        "credentials": [{
            "type": "password",
            "value": user_data.password,
            "temporary": False
        }]  
    }

    async with httpx.AsyncClient() as client:
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code not in (201, 204):
            logger.error(f"Keycloak response: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to create user in Keycloak")
        logger.info(f"User {user_data.username} data is stored in keycloak")

        # Create database session and mark user as synced
        db = SessionLocal()
        try:
            mark_user_as_synced(db, user_data.username)
            logger.info(f"User {user_data.username} data is stored in keycloak and marked as synced")
        except Exception as e:
            logger.error(f"Failed to mark user as synced: {str(e)}")
            raise
        finally:
            db.close()

