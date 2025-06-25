from sqlalchemy.orm import Session
from models.user_model import User


async def store_user_in_postgres(db: Session, user_data: dict) -> dict:

    # Convert camelCase to snake_case
    user_data["firstname"] = user_data.pop("firstName")
    user_data["lastname"] = user_data.pop("lastName")

    # Create a User instance with correct model fields
    db_user = User(
        username=user_data["username"],
        password=None,
        email=user_data["email"],
        firstname=user_data["firstname"],
        lastname=user_data["lastname"]
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_unsynced_users(db: Session):
    return db.query(User).filter(User.synced == False).all()

def mark_user_as_synced(db: Session, username: str):
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.synced = True
        db.commit()