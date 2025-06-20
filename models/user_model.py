from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, EmailStr
import uuid


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    username = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=False)
    firstname = Column(String, nullable=False)
    lastname = Column(String, nullable=False)
    password = Column(String, nullable=False)
    synced = Column(String, default="no")



# Pydantic Models
class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    firstName: str
    lastName: str

class TokenInput(BaseModel):
    token: str


