from pydantic import BaseModel, EmailStr
from datetime import datetime


# Register schema
class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str


# Login schema
class UserLogin(BaseModel):
    username: str
    password: str


# Token response schema
class Token(BaseModel):
    access_token: str
    token_type: str

# history bar
class FactCheckResponse(BaseModel):

    id: int
    claim: str
    similarity: float
    verdict: str
    created_at: datetime

    class Config:
        from_attributes = True