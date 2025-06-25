import bcrypt
import re
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)


# to hash the password [Optional in this project]
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


# Validate the password pattern during password reset via API routes
async def validate_password_pattern(password: str) -> str:
    """
    Validates password pattern:
    - Minimum 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 digit
    - At least 1 special character
    """
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&.])[A-Za-z\d@$!#%*?&.]{8,}$'
    if not re.match(pattern, password):
        logger.error(f"Password must contain at least 1 uppercase, 1 lowercase, 1 number, 1 special character, and be at least 8 characters long.")
        raise HTTPException(
            status_code=400,
            detail="Password must contain at least 1 uppercase, 1 lowercase, 1 number, 1 special character, and be at least 8 characters long."
        )
    logger.info(f"Valid password")
    return password
