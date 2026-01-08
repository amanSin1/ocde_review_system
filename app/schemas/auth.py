from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional,Literal

class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str
    role: Literal["student", "mentor"] = "student"  # admin NOT allowed

class UserOut(BaseModel):
    id : int
    email : EmailStr
    name : str
    role : str
    is_active : bool
    created_at : datetime
    class Config:
        from_attribute = True

class RegisterResponse(BaseModel):
    message: str
    user: UserOut
class LoginUser(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

    class Config:
        from_attribute = True


class TokenData(BaseModel):
    id : int | None = None