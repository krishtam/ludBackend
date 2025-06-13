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
        "ludora_backend.app.models.user",
        "ludora_backend.app.models.profile",
        "ludora_backend.app.models.progress",
        "ludora_backend.app.models.item",
        "ludora_backend.app.models.inventory",
        "ludora_backend.app.models.purchase",
        "ludora_backend.app.models.topic",
        "ludora_backend.app.models.question",
        "ludora_backend.app.models.quiz",
        "ludora_backend.app.models.minigame",
        "ludora_backend.app.models.leaderboard",
        "ludora_backend.app.models.quest" # Added quest model
    ] # Fully qualified model paths

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
