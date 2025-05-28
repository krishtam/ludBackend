"""
Database configuration and initialization for Ludora backend.
"""
from fastapi import FastAPI
from tortoise import Tortoise, run_async

from ludora_backend.app.core.config import settings

TORTOISE_ORM_CONFIG = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "models": { # 'models' is a conventional name for the app
            "models": settings.DB_MODELS, # This will now include aerich.models
            "default_connection": "default",
        },
    },
    "use_tz": False, # Explicitly set for clarity, though False is default
    # "timezone": "UTC", # Default, if use_tz is True
}

# This function is not used in the lifespan manager approach directly,
# but can be useful for other scripting or direct Tortoise interactions.
# The lifespan manager in main.py handles init and shutdown.
async def init_db_deprecated(app: FastAPI): # Renamed to avoid confusion
    """
    Initializes the database by registering Tortoise signal handlers.
    This approach is more common if not using FastAPI's lifespan.
    """
    @app.on_event("startup")
    async def startup():
        print("Initializing database (event handler approach)...")
        await Tortoise.init(
            config=TORTOISE_ORM_CONFIG
        )
        # Generate the schema if it doesn't exist
        # In a production app with migrations (Aerich), you might not want
        # to generate_schemas() on every startup after the initial setup.
        # Aerich handles schema changes.
        await Tortoise.generate_schemas()
        print("Database initialized (event handler approach).")

    @app.on_event("shutdown")
    async def shutdown():
        print("Closing database connections (event handler approach)...")
        await Tortoise.close_connections()
        print("Database connections closed (event handler approach).")

# Helper function to run Tortoise ORM operations in a standalone script if needed
async def run_async_main(coro):
    await Tortoise.init(config=TORTOISE_ORM_CONFIG)
    try:
        await coro
    finally:
        await Tortoise.close_connections()

# Example of how to use run_async_main:
# if __name__ == "__main__":
#     async def my_async_task():
#         # Your async ORM operations here
#         print("Running async task with Tortoise ORM")
#     run_async(run_async_main(my_async_task()))
