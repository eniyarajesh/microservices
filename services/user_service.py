from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user_model import UserCreate
from services.postgres_service import store_user_in_postgres, get_user_by_username
from auth.keycloak_auth import keycloak_user_exists, reset_user_password
import logging


logger = logging.getLogger(__name__)


async def register_user_data(user: UserCreate, db: Session):
    # 1. Check if user exists in PostgreSQL
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists in PostgreSQL")
    # 2. Check if user exists in Keycloak
    keycloak_user = await keycloak_user_exists(user.username)
    if keycloak_user:
        raise HTTPException(status_code=400, detail="User already exists in Keycloak")
    try:
        # Save user in PostgreSQL without password
        await store_user_in_postgres(db, user.dict())
        logger.info(f"User {user.username} stored in DB. Password setup email triggered.")
        return {"message": f"User {user.username} registered successfully"} 
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
    

# reset the password
async def handle_password_reset(username: str, new_password: str, db: Session):
    await reset_user_password(username, new_password)
    return {"message": "Password updated successfully"}

