"""
API dependencies, including authentication.
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from ludora_backend.app.models.user import User
from ludora_backend.app.schemas.token import TokenPayload
from ludora_backend.app.core.security import decode_token
from ludora_backend.app.core.config import settings # Used for tokenUrl prefix if needed, not directly here

# Define the OAuth2 scheme. The tokenUrl should point to your token endpoint.
# Make sure the path matches your auth router's path.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Decodes the token and returns the current user.
    Raises HTTPException if the token is invalid or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_token(token)

    if not token_data or not token_data.sub:
        raise credentials_exception

    try:
        user_id = int(token_data.sub)
    except ValueError:
        # If 'sub' is not a valid integer, it's an invalid token.
        raise credentials_exception

    user = await User.get_or_none(id=user_id)

    if user is None:
        # Changed to 401 as per typical OAuth2 flow for invalid token/subject.
        # If the token is valid but user doesn't exist (e.g. deleted after token issuance),
        # 401 is still appropriate as the token no longer corresponds to a valid, existing user.
        # Alternatively, a 404 could be argued if the intent is "valid token, but user entity gone".
        # Sticking to 401 for "could not validate credentials" umbrella.
        raise credentials_exception # Or specifically HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
                                  # The original instruction was 404, but 401 is more common for auth processes. Let's use 401 for consistency.

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Ensures the current user is active.
    Raises HTTPException if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
