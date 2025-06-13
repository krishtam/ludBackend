import pytest
from httpx import AsyncClient
from ludora_backend.app.models.user import User # For direct DB checks if needed

# Mark all tests in this module as asyncio
pytestmark = pytest.mark.asyncio

async def test_user_signup_success(client: AsyncClient):
    """Test successful user signup."""
    signup_data = {
        "username": "test_signup_user",
        "email": "testsignup@example.com",
        "password": "strongPassword123"
    }
    response = await client.post("/api/v1/auth/signup", json=signup_data)
    assert response.status_code == 200 # Assuming 200 OK for successful creation from your app

    user_data = response.json()
    assert user_data["username"] == signup_data["username"]
    assert user_data["email"] == signup_data["email"]
    assert "id" in user_data
    assert "hashed_password" not in user_data # Ensure password is not returned

    # Verify user is in the database
    db_user = await User.get_or_none(email=signup_data["email"])
    assert db_user is not None
    assert db_user.username == signup_data["username"]


async def test_user_signup_duplicate_username(client: AsyncClient, db_setup_module): # db_setup_module ensures clean db for this module
    """Test signup with a duplicate username."""
    # First user
    await client.post("/api/v1/auth/signup", json={
        "username": "duplicate_user",
        "email": "user1@example.com",
        "password": "password123"
    })

    # Second user with same username
    response = await client.post("/api/v1/auth/signup", json={
        "username": "duplicate_user", # Duplicate username
        "email": "user2@example.com",
        "password": "password456"
    })
    assert response.status_code == 400
    assert "Username already registered" in response.json()["message"] # Based on your auth.py error

async def test_user_signup_duplicate_email(client: AsyncClient, db_setup_module):
    """Test signup with a duplicate email."""
    # First user
    await client.post("/api/v1/auth/signup", json={
        "username": "user_A",
        "email": "duplicate@example.com", # Duplicate email
        "password": "password123"
    })

    # Second user with same email
    response = await client.post("/api/v1/auth/signup", json={
        "username": "user_B",
        "email": "duplicate@example.com", # Duplicate email
        "password": "password456"
    })
    assert response.status_code == 400
    assert "Email already registered" in response.json()["message"] # Based on your auth.py error

async def test_user_login_success(client: AsyncClient):
    """Test successful user login."""
    signup_data = {
        "username": "test_login_user",
        "email": "testlogin@example.com",
        "password": "loginPassword123"
    }
    # Create user first
    signup_response = await client.post("/api/v1/auth/signup", json=signup_data)
    assert signup_response.status_code == 200

    # Attempt login
    login_data = {"username": signup_data["username"], "password": signup_data["password"]}
    response = await client.post("/api/v1/auth/token", data=login_data) # OAuth2 expects form data

    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data
    assert token_data["token_type"] == "bearer"

async def test_user_login_incorrect_password(client: AsyncClient):
    """Test login with incorrect password."""
    signup_data = {
        "username": "test_badpass_user",
        "email": "testbadpass@example.com",
        "password": "correctPassword123"
    }
    await client.post("/api/v1/auth/signup", json=signup_data)

    login_data = {"username": signup_data["username"], "password": "incorrectPassword"}
    response = await client.post("/api/v1/auth/token", data=login_data)

    assert response.status_code == 401 # Unauthorized
    assert "Incorrect username or password" in response.json()["message"]

async def test_user_login_nonexistent_user(client: AsyncClient):
    """Test login for a user that does not exist."""
    login_data = {"username": "nonexistent_user", "password": "anypassword"}
    response = await client.post("/api/v1/auth/token", data=login_data)

    assert response.status_code == 401 # Unauthorized
    assert "Incorrect username or password" in response.json()["message"]

async def test_token_refresh_success(client: AsyncClient):
    """Test successful token refresh."""
    # 1. Signup and Login to get initial tokens
    signup_data = {"username": "refresh_user", "email": "refresh@example.com", "password": "refreshPassword123"}
    await client.post("/api/v1/auth/signup", json=signup_data)

    login_data = {"username": signup_data["username"], "password": signup_data["password"]}
    login_response = await client.post("/api/v1/auth/token", data=login_data)
    initial_tokens = login_response.json()
    initial_refresh_token = initial_tokens["refresh_token"]
    initial_access_token = initial_tokens["access_token"]

    # 2. Attempt to refresh token
    refresh_payload = {"refresh_token_str": initial_refresh_token} # Matches Body(..., embed=True)
    response_refresh = await client.post("/api/v1/auth/token/refresh", json=refresh_payload)

    assert response_refresh.status_code == 200
    new_tokens = response_refresh.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"
    assert new_tokens["access_token"] != initial_access_token # New access token should be different

async def test_token_refresh_invalid_token(client: AsyncClient):
    """Test token refresh with an invalid or expired refresh token."""
    refresh_payload = {"refresh_token_str": "this.is.an.invalid.refresh.token"}
    response_refresh = await client.post("/api/v1/auth/token/refresh", json=refresh_payload)

    assert response_refresh.status_code == 401 # Unauthorized
    assert "Invalid refresh token or missing subject" in response_refresh.json()["message"]

# Example of testing a protected route (if you have one set up, e.g., /users/me/profile)
# Add this if you have such an endpoint and it's simple enough for this initial test setup.
# async def test_protected_route_access(client: AsyncClient):
#     # Signup and login to get a token
#     signup_data = {"username": "protected_route_user", "email": "protected@example.com", "password": "password123"}
#     signup_resp = await client.post("/api/v1/auth/signup", json=signup_data)
#     user_id = signup_resp.json()["id"]

#     login_data = {"username": signup_data["username"], "password": signup_data["password"]}
#     login_resp = await client.post("/api/v1/auth/token", data=login_data)
#     access_token = login_resp.json()["access_token"]

#     # Access protected route
#     headers = {"Authorization": f"Bearer {access_token}"}
#     # Assuming /api/v1/users/me/profile is a protected route that returns profile info
#     response_me = await client.get("/api/v1/users/me/profile", headers=headers)
#     assert response_me.status_code == 200
#     assert response_me.json()["user_id"] == user_id # Assuming ProfileRead schema has user_id
#     assert response_me.json()["email"] == signup_data["email"] # UserRead has email, ProfileRead might from user
#     # The exact assertion depends on the response model of your /users/me/profile endpoint
#     # If it's ProfileRead, it should contain user_id.
#     # The ProfileRead schema: id, user_id, current_streak, max_streak, in_app_currency, created_at, updated_at, first_name, last_name, avatar_url, bio
#     # So, we might assert on user_id.
#     # To get the user's email in the profile response, UserProfile model would need to expose it or UserRead would be nested.
#     # The ProfileRead schema has user_id, so we can check that.
#     # The UserProfile object itself has user_id as a direct field.
#     # Let's check if user_id is correctly populated in the response.
#     # Profile model has a user_id field from the OneToOne.
#     # ProfileRead schema has user_id.
#     # The /users/me/profile endpoint returns ProfileRead which should have user_id.
#     # The current UserProfile.get_or_create(user=current_user) in users.py endpoint
#     # should ensure profile.user_id is set.
#     # Let's verify the user_id from the profile response.
#     profile_data = response_me.json()
#     assert profile_data["user_id"] == user_id
#     # Also test the email which should be part of the user associated with the profile
#     # This requires the UserRead schema (or parts of it) to be part of ProfileRead,
#     # or for ProfileRead to include email directly.
#     # The current ProfileRead does NOT include email. It includes user_id.
#     # The User model associated with current_user has the email.
#     # The UserProfile model itself doesn't store email.
#     # So, asserting email directly from profile_data might fail unless ProfileRead is changed.
#     # For now, user_id check is sufficient as a basic protected route test.
