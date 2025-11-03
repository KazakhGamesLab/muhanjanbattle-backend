from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    telegram_id: int
    twitch_nickname: str
    first_name: str
    telegram_username: Optional[str] = None

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True