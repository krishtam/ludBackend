import pytest
import asyncio
import os
from fastapi import FastAPI
from httpx import AsyncClient
from tortoise import Tortoise

# Import the main FastAPI app instance
from ludora_backend.app.main import app
# Import the original TORTOISE_ORM_CONFIG to get model paths, etc.
from ludora_backend.app.core.db import TORTOISE_ORM_CONFIG as ORIGINAL_TORTOISE_CONFIG
from ludora_backend.app.core.config import settings # To potentially override settings

# --- Test Database Configuration ---
TEST_DATABASE_URL = "sqlite://:memory:"

# Construct a test-specific TORTOISE_ORM_CONFIG
# This ensures we use the same model paths as the main application
# but connect to an in-memory SQLite database for tests.
TEST_TORTOISE_ORM_CONFIG = {
    "connections": {"default": TEST_DATABASE_URL},
    "apps": {
        "models": {
            "models": ORIGINAL_TORTOISE_CONFIG["apps"]["models"]["models"], # Use models from original config
            "default_connection": "default",
        },
    },
    "use_tz": False, # Explicitly set for tests
}

async def init_test_db():
    """Initializes the test database with the test configuration."""
    await Tortoise.init(config=TEST_TORTOISE_ORM_CONFIG)
    await Tortoise.generate_schemas()
    print("Test database initialized and schemas generated.")

async def close_test_db():
    """Closes connections to the test database."""
    await Tortoise.close_connections()
    print("Test database connections closed.")


# --- Pytest Fixtures ---

@pytest.fixture(scope="session")
def event_loop():
    """
    Creates an instance of the default event loop for each test session.
    pytest-asyncio default behavior handles this, but explicit definition is fine.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()

# Fixture to manage the database initialization and teardown for a module/session.
# Using "module" scope for db to speed up tests, assuming tests don't interfere
# with each other's data too much, or they clean up after themselves.
# For fully isolated tests, "function" scope might be preferred but is slower.
@pytest.fixture(scope="module")
async def db_setup_module():
    """Manages database setup and teardown for a test module."""
    print("Initializing DB for module...")
    await init_test_db()
    yield
    print("Closing DB for module...")
    await close_test_db()


@pytest.fixture(scope="function") # Changed to function scope for client to ensure clean state for each test
async def client(db_setup_module): # Depend on db_setup_module to ensure DB is up
    """
    Provides an AsyncClient instance for making API requests to the test app.
    Ensures the FastAPI app's lifespan events for DB init/shutdown are handled
    or bypassed correctly for testing.
    """
    # How FastAPI app's lifespan is handled during testing:
    # The AsyncClient, by default, does run startup/shutdown events of the app.
    # Our main app has a lifespan manager that initializes Tortoise with the
    # production DB settings. This is problematic for tests.
    #
    # Strategy:
    # 1. The `db_setup_module` fixture explicitly initializes Tortoise with
    #    `TEST_TORTOISE_ORM_CONFIG` *before* the app or client is created.
    #    This means Tortoise is already configured with the in-memory DB
    #    when the app's lifespan manager (if it runs) tries to init Tortoise.
    # 2. To prevent the app's own lifespan DB init from conflicting or re-initing
    #    with production settings, we need to ensure it either:
    #    a) Also uses the test DB settings (e.g., by checking an env var like `TESTING=True`).
    #    b) Its DB init part is effectively skipped or becomes a no-op if Tortoise is already inited.
    #
    # Tortoise.init has a safeguard: `if cls._inited: return`.
    # So, if `init_test_db()` correctly sets `Tortoise._inited = True`,
    # the app's lifespan `Tortoise.init()` should be a no-op.
    # We rely on `init_test_db()` running first and setting Tortoise up.

    # Override settings if necessary (e.g., for JWT tokens if they use settings directly)
    # For this example, we'll assume the default settings are fine for token generation,
    # or that tests mock `app.core.security.settings` if needed.
    # A more robust way would be to use dependency overrides for settings in tests.

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    # Teardown for function-scoped client (if any needed beyond db_setup_module)
    # If db_setup_module was function-scoped, close_test_db would be here.
    # Since db_setup_module is module-scoped, db connections are closed after all tests in the module.
