from fastapi import APIRouter, HTTPException, Depends
from models.user_model import UserCreate
from services.user_service import get_user_by_username
from services.postgres_service import store_user_in_postgres
from auth.keycloak_auth import keycloak_user_exists
from sqlalchemy.orm import Session
from db.postgres import get_db
from redis_cache.user_cache import redis_client  # Redis client instance
import json
import logging

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    # 1. Check if user exists in PostgreSQL
    db_user = get_user_by_username(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already exists in PostgreSQL")

    # 2. Check if user exists in Keycloak
    keycloak_user = await keycloak_user_exists(user.username)
    if keycloak_user:
        raise HTTPException(status_code=400, detail="User already exists in Keycloak")

    try:
        # Step 1: Cache raw user data (with password) in Redis
        redis_client.set(user.username, json.dumps(user.dict()))

        # Step 2: Store user in PostgreSQL without password
        user_data = user.dict()
        await store_user_in_postgres(db, user_data)
        logger.info(f"🗃️ User {user.username} stored in PostgreSQL (no password) and cached in Redis.")

    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed.")

    return {"message": f"User {user.username} successfully registered and queued for Keycloak sync."}
