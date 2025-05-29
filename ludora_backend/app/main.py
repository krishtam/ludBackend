"""
Main application file for Ludora backend.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from ludora_backend.app.api.v1.endpoints import auth as auth_router
from ludora_backend.app.api.v1.endpoints import users as user_profile_router
from ludora_backend.app.api.v1.endpoints import progress as learning_progress_router
from ludora_backend.app.api.v1.endpoints import shop as shop_router
from ludora_backend.app.api.v1.endpoints import inventory as inventory_router
from ludora_backend.app.api.v1.endpoints import questions as questions_router
from ludora_backend.app.api.v1.endpoints import quizzes as quizzes_router
from ludora_backend.app.core.db import TORTOISE_ORM_CONFIG # Import config directly for lifespan
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

app = FastAPI(title="Ludora Backend", lifespan=lifespan)

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


# Placeholder for root endpoint, can be expanded later
@app.get("/")
async def root():
    return {"message": "Welcome to Ludora Backend API"}
