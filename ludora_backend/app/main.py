"""
Main application file for Ludora backend.
"""
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from slowapi import Limiter, _rate_limit_exceeded_handler # Use _rate_limit_exceeded_handler for default behavior or define custom
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded # Import this for the handler

from ludora_backend.app.api.v1.endpoints import auth as auth_router
from ludora_backend.app.api.v1.endpoints import users as user_profile_router
from ludora_backend.app.api.v1.endpoints import progress as learning_progress_router
from ludora_backend.app.api.v1.endpoints import shop as shop_router
from ludora_backend.app.api.v1.endpoints import inventory as inventory_router
from ludora_backend.app.api.v1.endpoints import questions as questions_router
from ludora_backend.app.api.v1.endpoints import quizzes as quizzes_router
from ludora_backend.app.api.v1.endpoints import analytics as analytics_router
from ludora_backend.app.api.v1.endpoints import minigames as minigames_router
from ludora_backend.app.api.v1.endpoints import leaderboards as leaderboards_router
from ludora_backend.app.core.db import TORTOISE_ORM_CONFIG
from ludora_backend.app.exceptions import http_exception_handler, general_exception_handler, validation_exception_handler # Import handlers
from tortoise import Tortoise

@asynccontextmanager
async def lifespan(app_instance: FastAPI): # Renamed app to app_instance to avoid conflict
    # Initialize DB
    print("Initializing database (lifespan)...")
    await Tortoise.init(config=TORTOISE_ORM_CONFIG)
    # Generate the schema if it doesn't exist.
    # In a production app with migrations (Aerich), you might not want
    # to generate_schemas() on every startup after the initial setup.
    # Aerich handles schema changes.
    await Tortoise.generate_schemas()
    print("Database initialized (lifespan).")
    yield
    # Close DB connections
    print("Closing database connections (lifespan)...")
    await Tortoise.close_connections()
    print("Database connections closed (lifespan).")

# Define exception handlers to be used in the FastAPI app
exception_handlers_config = {
    HTTPException: http_exception_handler,
    RequestValidationError: validation_exception_handler,
    Exception: general_exception_handler,
    RateLimitExceeded: _rate_limit_exceeded_handler # Default handler, or use a custom one below
}

# Custom rate limit exceeded handler (optional, if _rate_limit_exceeded_handler is not sufficient)
# async def custom_rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
#     return JSONResponse(
#         status_code=429,
#         content={"message": f"Rate limit exceeded: {exc.detail}", "type": "RateLimitExceeded"}
#     )
# # If using custom handler, update exception_handlers_config:
# # exception_handlers_config[RateLimitExceeded] = custom_rate_limit_exceeded_handler

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])

app = FastAPI(
    title="Ludora Backend", 
    lifespan=lifespan,
    exception_handlers=exception_handlers_config # Register handlers
)

# Add limiter to app state
app.state.limiter = limiter

# Authentication router
app.include_router(auth_router.router, prefix="/api/v1/auth", tags=["Authentication"])

# User Profile router
app.include_router(user_profile_router.router, prefix="/api/v1", tags=["User Profile"])

# Learning Progress router
app.include_router(learning_progress_router.router, prefix="/api/v1", tags=["Learning Progress"])

# Shop router
app.include_router(shop_router.router, prefix="/api/v1/shop", tags=["Shop"])

# Inventory router
app.include_router(inventory_router.router, prefix="/api/v1/inventory", tags=["Inventory"])

# Question router
app.include_router(questions_router.router, prefix="/api/v1/q", tags=["Questions & Topics"]) # Using /q as a shorter prefix

# Quiz router
app.include_router(quizzes_router.router, prefix="/api/v1/quizzes", tags=["Quizzes"])

# Analytics router
app.include_router(analytics_router.router, prefix="/api/v1", tags=["User Analytics & Recommendations"])

# Minigames router
app.include_router(minigames_router.router, prefix="/api/v1", tags=["Minigames"])

# Leaderboards router
app.include_router(leaderboards_router.router, prefix="/api/v1", tags=["Leaderboards"])


# Placeholder for root endpoint, can be expanded later
@app.get("/")
async def root():
    return {"message": "Welcome to Ludora Backend API"}
