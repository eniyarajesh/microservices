from sqlalchemy import Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr, field_validator
from utils.username_pattern import validate_username
from utils.email_pattern import validate_email_pattern


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(String, nullable=True) 
    synced = Column(Boolean, default=False)


# Pydantic Models
class UserCreate(BaseModel):
    username: str
    # password: str = Field(..., min_length=8)
    email: EmailStr
    firstName: str
    lastName: str

    
    @field_validator('username')
    @classmethod
    def username_pattern_validator(cls, value:str) -> str:
        return validate_username(value)

    # @field_validator('password')
    # @classmethod
    # def password_pattern_validator(cls, value: str) -> str:
    #     return validate_password_pattern(value)
    
    @field_validator('email')
    @classmethod
    def email_pattern_validator(cls, value: str) -> str:
        return validate_email_pattern(value)


class TokenInput(BaseModel):
    token: str

class EmailRequest(BaseModel):
    username: str
    email: EmailStr

class PasswordResetRequest(BaseModel):
    username: str
    new_password: str