import re
from fastapi import HTTPException

def validate_email_pattern(email: str) -> str:
    """
    Validates email pattern.
    Ensures email has proper format (example@domain.com) with optional custom rules.
    """
    email_regex = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
    if not email_regex.match(email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format. Must be in format like example@domain.com"
        )
    return email


