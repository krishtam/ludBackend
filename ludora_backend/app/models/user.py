"""
User model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields
from tortoise.signals import post_save
from typing import Type, Optional # Optional is already imported in Python 3.9+ by default for type hints, but explicit is fine.
from tortoise import BaseDBAsyncClient # For type hinting using_db

class User(Model):
    """
    User model.
    """
    id = fields.IntField(pk=True, generated=True)
    username = fields.CharField(max_length=255, unique=True, index=True)
    email = fields.CharField(max_length=255, unique=True, index=True)
    hashed_password = fields.CharField(max_length=255)
    is_active = fields.BooleanField(default=True)
    is_superuser = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.username

# Signal to create a UserProfile automatically when a User is created.
@post_save(User)
async def create_user_profile(
    sender: "Type[User]", # The model class that sent the signal.
    instance: User,      # The actual instance of the model that was saved.
    created: bool,       # True if a new record was created, False if an existing record was updated.
    using_db: "Optional[BaseDBAsyncClient]", # The database connection used.
    update_fields: list[str], # List of fields that were updated (empty if created).
) -> None:
    if created:
        # Lazy import to avoid circular dependencies if UserProfile also imports User
        from ludora_backend.app.models.profile import UserProfile 
        await UserProfile.create(user=instance)
        # Optional: print a confirmation or log this event
        print(f"UserProfile created for new user {instance.username} (ID: {instance.id})")
