from fastapi import HTTPException
from sqlalchemy.orm import Session
from models.user_model import User
from models.user_model import UserCreate
from redis_cache.user_cache import cache_user_data
from services.postgres_service import store_user_in_postgres
from typing import Dict
from db.postgres import SessionLocal
import uuid
import logging


logger = logging.getLogger(__name__)


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_unsynced_users(db: Session):
    return db.query(User).filter(User.synced == "no").all()

def mark_user_as_synced(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.synced = "yes"
        db.commit()



'''
async def register_user_service(user: UserCreate):
    db = SessionLocal()
    try:
        # Convert user (Pydantic) to dict and pass to DB function
        user_data = user.dict()
        store_user_in_postgres(db, user_data)

        cache_user_data(user)  # raw user with plaintext password
        logger.info(f"🗃️ User {user.username} stored in PostgreSQL and cached.")
        
    except Exception as e:
        logger.error(f"❌ Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed.")
    finally:
        db.close()
    return {"message": f"User {user.username} successfully registered and queued for Keycloak sync."}
'''