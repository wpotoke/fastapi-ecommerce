from datetime import datetime
from pydantic import BaseModel, Field


class RefreshTokenBase(BaseModel):
    token: str = Field(min_length=145, max_length=200)
    user_id: int
    expires_at: datetime


class TokenGroup(BaseModel):
    access_token: str
    refresh_token: RefreshTokenBase


class RefreshTokenRequest(BaseModel):
    refresh_token: str
