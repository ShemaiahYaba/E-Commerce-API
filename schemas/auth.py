"""Auth request/response schemas."""

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Login payload."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT and user in auth responses."""

    access_token: str
    token_type: str = "Bearer"
    user: dict
