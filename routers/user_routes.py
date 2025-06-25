from fastapi import APIRouter, HTTPException, Depends
from models.user_model import UserCreate, PasswordResetRequest
from services.user_service import register_user_data, handle_password_reset
from services.reset_email_service import reset_password_email
from sqlalchemy.orm import Session
from db.postgres import get_db
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/token")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        return await register_user_data(user, db)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    

@router.post("/send-password-email")
async def send_password_email(username: str):
    try:
        await reset_password_email(username)
        return {"message": f"Email sent to {username}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
    

@router.post("/reset-password")
async def reset_password(data: PasswordResetRequest, db: Session = Depends(get_db)):
    try:
        result = await handle_password_reset(data.username, data.new_password, db)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal error during password reset")

