from sqlalchemy.orm import Session
from utils.email_pswd_pattern import hash_password
from models.user_model import User


def store_user_in_postgres(db: Session, user_data: dict) -> dict:

    user_data["password"] = hash_password(user_data["password"])

    # Convert camelCase to snake_case
    user_data["firstname"] = user_data.pop("firstName")
    user_data["lastname"] = user_data.pop("lastName")

    # Create a User instance with correct model fields
    db_user = User(
        username=user_data["username"],
        password=hash_password(user_data["password"]),
        email=user_data["email"],
        firstname=user_data["firstname"],
        lastname=user_data["lastname"]
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user