import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models.user_model import UserCreate
import httpx
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM
from logs.logging_config import setup_logger
import logging 

logger = setup_logger()


token_scheme = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_scheme)):
    token = credentials.credentials  # Extract the actual token

    url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
    headers={"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
    except Exception as e:
        print("Exception while calling Keycloak:", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail=f"Keycloak response: {response.status_code} - {response.text}"
        )
    
    return response.json()


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

async def keycloak_user_exists(username: str) -> bool:
    token = await get_admin_token()
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={username}"
        response = await client.get(url, headers=headers)
        return bool(response.json())

async def create_keycloak_user(user_data: UserCreate):
    token = await get_admin_token()
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
        # response.raise_for_status()
        if response.status_code not in (201, 204):
            logger.error(f"Keycloak response: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail="Failed to create user in Keycloak")
        

    # async with httpx.AsyncClient() as client:
    #     create_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
    #     create_response = await client.post(create_url, json=payload, headers=headers)
    #     create_response.raise_for_status()

    #     # Step 2: Get user ID
    #     get_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users?username={user_data.username}"
    #     get_response = await client.get(get_url, headers=headers)
    #     get_response.raise_for_status()
    #     user_list = get_response.json()
    #     if not user_list:
    #         raise HTTPException(status_code=404, detail="User not found after creation")

    #     user_id = user_list[0]['id']

    #     # Step 3: Clear requiredActions (like 'UPDATE_PASSWORD')
    #     update_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}"
    #     update_payload = {
    #         "requiredActions": []
    #     }
    #     update_response = await client.put(update_url, json=update_payload, headers=headers)
    #     update_response.raise_for_status()
















# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
# from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM
# from services.auth_service import validate_token_with_keycloak
# import httpx

# # oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")
# # security = HTTPBearer(auto_error=True)

# token_scheme = HTTPBearer()

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(token_scheme)):
#     token = credentials.credentials  # Extract the actual token

#     url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/userinfo"
#     headers={"Authorization": f"Bearer {token}"}

#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(url, headers=headers)
#     except Exception as e:
#         print("Exception while calling Keycloak:", e)
#         raise HTTPException(status_code=500, detail="Internal Server Error")

#     if response.status_code != 200:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED, 
#             detail=f"Keycloak response: {response.status_code} - {response.text}"
#         )
    
#     return response.json()


