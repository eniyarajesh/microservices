import re
from fastapi import HTTPException


# validate username
def validate_username(username: str) -> str:
    if " " in username:
         raise ValueError("Username must not contain spaces.")
    return username
