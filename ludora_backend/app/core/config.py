"""
Configuration settings for Ludora backend.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings.
    """
    SECRET_KEY: str = "YOUR_SECRET_KEY_HERE_PLEASE_CHANGE_ME"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # Database settings
    DATABASE_URL: str = "sqlite://./ludora_test.db"
    DB_MODELS: list[str] = [
        "aerich.models", 
        "app.models.user", 
        "app.models.profile", 
        "app.models.progress",
        "app.models.item",
        "app.models.inventory",
        "app.models.purchase"
    ] # Add aerich.models for migrations and new models

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
