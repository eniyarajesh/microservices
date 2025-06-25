import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user_model import User
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM
from utils.pswd_pattern import validate_password_pattern
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
    

# get user id
async def get_user_id(token, username):
    url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"username": username}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code == 200:
            users = response.json()

            exact_users = [
                user for user in users if user.get("username", "").lower() == username.lower()
            ]

            if exact_users:
                user_id = exact_users[0]['id']
                logger.info(f"✅ User ID fetched for user: {username} - ID: {user_id}")
                return user_id
            else:
                logger.error(f"❌ User '{username}' not found in Keycloak.")
                raise HTTPException(
                    status_code=404,
                    detail=f"User '{username}' not found in Keycloak."
                )
        else:
            logger.error(f"❌ Failed to fetch user ID for '{username}'. Status: {response.status_code}: {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch user info from Keycloak")


# get admin token
async def get_admin_token():
    async with httpx.AsyncClient() as client:
        url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
        data = {
            "grant_type": "password",
            "client_id": "admin-cli",
            "username": os.getenv("KEYCLOAK_ADMIN"),
            "password": os.getenv("KEYCLOAK_ADMIN_PASSWORD")
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
async def sync_user_to_keycloak(user_data: User):
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
        "firstName": user_data.firstname,
        "lastName": user_data.lastname,
        "requiredActions": ["UPDATE_PASSWORD"]
        # "credentials": [{
        #     "type": "password",
        #     "value": DEFAULT_TEMP_PASSWORD,
        #     "temporary": True
        # }]  
    }

    async with httpx.AsyncClient() as client:

        # check_username_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={user_data.username}"
        # response_username = await client.get(check_username_url, headers=headers)
        # if response_username.status_code != 200:
        #     raise HTTPException(status_code=500, detail="Failed to check username in Keycloak")
        # if response_username.json():
        #     raise HTTPException(status_code=400, detail="Username already exists in Keycloak")

        # # Check for existing email
        # check_email_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?email={user_data.email}"
        # response_email = await client.get(check_email_url, headers=headers)
        # if response_email.status_code != 200:
        #     raise HTTPException(status_code=500, detail="Failed to check email in Keycloak")
        # if response_email.json():
        #     raise HTTPException(status_code=400, detail="Email already exists in Keycloak")
        
        
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        response = await client.post(url, json=payload, headers=headers)
        if response.status_code not in (201, 204):
            logger.error(f"❌ Keycloak response: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to create user in Keycloak")
    
    logger.info(f"✅ User {user_data.username} data is stored in keycloak")

      
# Reset user password in Keycloak
async def reset_user_password(username: str, new_password: str):
    await validate_password_pattern(new_password)
    token = await get_admin_token()
    
    # Get user ID by username
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={username}"
        response = await client.get(url, headers=headers)

        if response.status_code != 200 or not response.json():
            raise HTTPException(status_code=404, detail="User not found in Keycloak")

        user_id = response.json()[0]["id"]

        # Reset password (permanent)
        reset_payload = {
            "type": "password",
            "value": new_password,
            "temporary": False
        }

        reset_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/reset-password"
        reset_response = await client.put(reset_url, headers=headers, json=reset_payload)

        if reset_response.status_code != 204:
            raise HTTPException(status_code=reset_response.status_code, detail="Failed to reset password in Keycloak")
        
        return {"status": "success", "message": f"Password reset for {username}"}
