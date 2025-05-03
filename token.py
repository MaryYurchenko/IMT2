# app/schemas/token.py
from __future__ import annotations
from pydantic.v1 import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[int] = None