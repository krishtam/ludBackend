import pytest
from datetime import timedelta, datetime, timezone # Ensure timezone is imported for aware datetime objects

from ludora_backend.app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from ludora_backend.app.core.config import settings # settings will be used for token generation
from ludora_backend.app.schemas.token import TokenPayload

def test_password_hashing():
    password = "testpassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_jwt_token_creation_decoding():
    user_id = "test_user_sub_1"
    token_data = {"sub": user_id}
    
    # Access token
    access_token = create_access_token(data=token_data)
    decoded_payload = decode_token(access_token)
    
    assert decoded_payload is not None
    assert decoded_payload.sub == user_id
    # Check if 'exp' is present and is a future timestamp
    assert decoded_payload.exp is not None
    assert datetime.fromtimestamp(decoded_payload.exp, tz=timezone.utc) > datetime.now(timezone.utc)

    # Refresh token (similar logic, potentially longer expiry)
    refresh_token = create_refresh_token(data=token_data)
    decoded_refresh_payload = decode_token(refresh_token)

    assert decoded_refresh_payload is not None
    assert decoded_refresh_payload.sub == user_id
    assert decoded_refresh_payload.exp is not None
    assert datetime.fromtimestamp(decoded_refresh_payload.exp, tz=timezone.utc) > datetime.now(timezone.utc)


def test_expired_jwt_token():
    user_id = "test_user_sub_expired"
    token_data = {"sub": user_id}
    
    # Create an already expired access token
    # timedelta is negative, so token is created for the past
    expired_access_token = create_access_token(data=token_data, expires_delta=timedelta(seconds=-3600))
    assert decode_token(expired_access_token) is None, "Expired access token should return None"

    # Create an already expired refresh token
    expired_refresh_token = create_refresh_token(data=token_data, expires_delta=timedelta(seconds=-3600))
    assert decode_token(expired_refresh_token) is None, "Expired refresh token should return None"

def test_invalid_jwt_token():
    invalid_token = "this.is.not.a.valid.token"
    assert decode_token(invalid_token) is None

    # Token with valid structure but wrong signature/secret
    user_id = "test_user_sub_invalid_sig"
    token_data = {"sub": user_id, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}
    
    # Simulate a token encoded with a different key or algorithm (not easily done without re-encoding)
    # For simplicity, we'll assume decode_token handles various JWTError scenarios.
    # A more direct test for signature might involve manually creating a token with a different key.
    # For now, an invalid format is a basic check.
    # A token that's just slightly malformed:
    slightly_malformed_token = create_access_token(data={"sub": user_id}) + "invalidpart"
    assert decode_token(slightly_malformed_token) is None

def test_token_payload_without_sub():
    # Create a token that's technically valid JWT but misses the 'sub' claim
    # This requires manually crafting the payload for jwt.encode
    from jose import jwt # Import directly for this specific test case
    
    payload_no_sub = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        # "sub": "some_user" # 'sub' is missing
    }
    token_no_sub = jwt.encode(payload_no_sub, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    assert decode_token(token_no_sub) is None, "Token without 'sub' should be invalid"

def test_token_payload_without_exp():
    # Create a token that's technically valid JWT but misses the 'exp' claim
    from jose import jwt # Import directly for this specific test case
    
    payload_no_exp = {
        "sub": "some_user"
        # "exp": ... # 'exp' is missing
    }
    # Note: jwt.decode itself might not raise an error if 'exp' is missing,
    # but our decode_token function has an explicit check for payload.get("exp") is None.
    token_no_exp = jwt.encode(payload_no_exp, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    assert decode_token(token_no_exp) is None, "Token without 'exp' should be invalid by our custom check"
