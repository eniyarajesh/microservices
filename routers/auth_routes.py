from fastapi import APIRouter, HTTPException, Depends
from models.user_model import TokenInput
from fastapi.security import OAuth2PasswordBearer
from auth.keycloak_auth import get_current_user
from services.auth_service import validate_token_with_keycloak, get_access_token
from config.settings import KEYCLOAK_URL, KEYCLOAK_REALM, KEYCLOAK_CLIENT_ID, KEYCLOAK_CLIENT_SECRET
import httpx

router = APIRouter(tags=["Authentication"])


@router.post("/token")
async def get_token(user_name: str, password: str):
    try:
        return await get_access_token(user_name, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/validate-token")
async def validate_token(user_info: dict = Depends(get_current_user)):
    """
    Protected endpoint - Requires Bearer token. Will show 🔒 in Swagger.
    """
    return {
        "status": "Authorized ✅",
        "user_info": user_info
    }

