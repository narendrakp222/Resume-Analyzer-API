from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, json_schema_extra={"example": "johndoe"})
    email: EmailStr = Field(..., json_schema_extra={"example": "john@example.com"})
    password: str = Field(..., min_length=6, max_length=100, json_schema_extra={"example": "securePassword123"})


class UserLogin(BaseModel):
    username_or_email: str = Field(..., json_schema_extra={"example": "johndoe"})
    password: str = Field(..., json_schema_extra={"example": "securePassword123"})


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
