from pydantic import BaseModel, HttpUrl, field_validator
from datetime import datetime, timezone
from typing import Optional

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class LinkBase(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = None
    expires_at: Optional[datetime] = None

    def validate_expires_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            if v.tzinfo is None:
                v = v.replace(tzinfo=timezone.utc)
                
            now = datetime.now(timezone.utc)
            if v <= now:
                raise ValueError("Expiration date must be in the future")

            return v.replace(second=0, microsecond=0)
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LinkCreate(LinkBase):
    pass

class Link(LinkBase):
    id: int
    short_code: str
    created_at: datetime
    last_accessed: Optional[datetime]
    access_count: int
    user_id: Optional[int]

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
