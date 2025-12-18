"""Schemas for the API authenticator module."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for OAuth2 token response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Schema for OAuth2 token data."""

    username: str | None = None
    scopes: list[str] = []


class TokenPayload(BaseModel):
    """Schema for OAuth2 token payload."""

    sub: str
    scopes: list[str]


class TokenRequest(BaseModel):
    """Schema for OAuth2 token request."""

    username: str
    password: str
