from fastapi import APIRouter, HTTPException, Depends, Request
from models.user_model import UserCreate
from sqlalchemy.orm import Session
from db.postgres import SessionLocal, get_db
from services.user_service import get_user_by_username, register_user_service
# from services.auth_service import store_user_in_postgres
from utils.email_pswd_pattern import hash_password
from auth.keycloak_auth import keycloak_user_exists
from logs.logging_config import setup_logger
import logging

router = APIRouter()

logger = setup_logger()

 

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

    # 3. Register user (store in DB + cache raw data)
    response = await register_user_service(user)
    logger.info(f"🗃️  User {user.username} registered in PostgreSQL. Awaiting Keycloak sync...")

    return response

    # return {"message": f"User {user.username} registered in PostgreSQL. Awaiting Keycloak sync."}

    # return await register_user_service(user)


'''

@router.post("/register")
async def register_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    user = await request.json()
    username = user["username"]

    if get_user_by_username(db, username):
        raise HTTPException(status_code=400, detail="User already exists in PostgreSQL")
    
    if await keycloak_user_exists(username):
        raise HTTPException(status_code=400, detail="User already exists in Keycloak")

    # user["password"] = hash_password(user["password"])

    create_user_in_postgres(db, user)
    # store_user_in_postgres(user)
    logger.info(f"🗃️  User {username} registered in PostgreSQL. Awaiting Keycloak sync...")

    return {"message": f"User {username} registered in PostgreSQL. Awaiting Keycloak sync."}

'''











# from fastapi import APIRouter, Depends, HTTPException
# from models.user_model import UserCreate, UserOut
# from services.user_service import create_user
# from auth.keycloak_auth import get_current_user

# router = APIRouter()

# @router.post("/register", response_model=UserOut)
# async def register_user(user: UserCreate):
#     try:
#         return await create_user(user)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))



