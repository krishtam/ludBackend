"""
Authentication endpoints for Ludora backend.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.security import OAuth2PasswordRequestForm

from ludora_backend.app.schemas.user import UserCreate, UserRead
from ludora_backend.app.schemas.token import Token, TokenPayload
from ludora_backend.app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from ludora_backend.app.models.user import User # For type hinting and ORM operations later
from ludora_backend.app.core.config import settings

router = APIRouter()

@router.post("/signup", response_model=UserRead)
async def signup(user_in: UserCreate):
    """
    Handles user registration.
    """
    # Check if user with the given username or email already exists.
    if await User.exists(username=user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if await User.exists(email=user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pword = hash_password(user_in.password)
    user_data = user_in.model_dump(exclude={"password"}) # Pydantic v2
    
    # Create the user in the database
    # Tortoise models are Pydantic-compatible, so we can directly return them
    # if the response_model is set up correctly (e.g. UserRead with orm_mode=True)
    db_user = await User.create(**user_data, hashed_password=hashed_pword)
    
    # UserRead will automatically convert from the ORM model if Config.orm_mode = True
    # If UserRead is not from_orm compatible or you need specific fields,
    # you would manually construct UserRead here.
    # For this setup, UserRead should be orm_mode compatible.
    return db_user # This works because UserRead has orm_mode = True

@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Handles user login and token generation.
    Standard path for OAuth2 token endpoints.
    """
    # Fetch user by username (or email, if you want to allow that)
    user = await User.get_or_none(username=form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, # Unauthorized
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user") # Bad Request

    user_identity = str(user.id) # Use user ID for the 'sub' claim in JWT

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_identity}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(data={"sub": user_identity}, expires_delta=refresh_token_expires)

    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")

@router.post("/token/refresh", response_model=Token)
async def refresh_token(refresh_token_str: str = Body(..., embed=True)):
    """
    Handles token refresh.
    """
    token_data = decode_token(refresh_token_str)

    if not token_data or not token_data.sub:
        raise HTTPException(
            status_code=401, # Unauthorized
            detail="Invalid refresh token or missing subject",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id_int = int(token_data.sub)
    except ValueError:
        raise HTTPException(
            status_code=401, # Unauthorized
            detail="Invalid user identifier in token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await User.get_or_none(id=user_id_int)

    if not user:
        raise HTTPException(
            status_code=401, # Unauthorized
            detail="User not found for refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user") # Bad Request

    user_identity = str(user.id)

    new_access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": user_identity}, expires_delta=new_access_token_expires)

    # Issue a new refresh token as well
    new_refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    new_refresh_token = create_refresh_token(data={"sub": user_identity}, expires_delta=new_refresh_token_expires)

    return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer")
