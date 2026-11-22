"""Authentication boundary, deliberately closed in production until integrated."""

from fastapi import HTTPException, Request, status


async def require_application_access(request: Request) -> None:
    """Allow development; deny production until a real identity verifier replaces this dependency.

    The future verifier must validate the issuer, audience, signature and expiry,
    then enforce application permissions. Never trust an arbitrary user header.
    """
    if request.app.state.settings.environment == "production":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Application authentication has not been configured",
        )
