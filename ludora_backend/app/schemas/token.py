"""
Token schemas for Ludora backend.
"""
from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Schema for Token data.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    """
    Schema for Token payload data.
    """
    sub: Optional[str] = None
    exp: Optional[int] = None
