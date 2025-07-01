from pydantic import BaseModel, EmailStr, Field
from bson import ObjectId


class UserModel(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr = Field(..., description="User's unique email")
    password: str = Field(..., min_length=6)
