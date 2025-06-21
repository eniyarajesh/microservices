from fastapi import APIRouter, HTTPException, Depends
from auth.keycloak_auth import get_current_user
from services.auth_service import get_access_token

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

