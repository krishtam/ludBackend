"""
Item model for Ludora backend shop.
"""
from tortoise.models import Model
from tortoise import fields
from .enums import ItemType # Relative import for enums within the same 'models' package

class Item(Model):
    """
    Item model.
    """
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(null=True)
    price = fields.IntField(description="Price in in-app currency")
    item_type = fields.CharEnumField(ItemType, max_length=50)
    # Using metadata_ as the field name in the model
    # and "metadata" as the actual database column name.
    # This helps avoid potential conflicts with a Pydantic 'metadata' attribute/method.
    metadata_ = fields.JSONField(null=True, description="Type-specific attributes, e.g., {'duration': '30m'} for a power-up", name="metadata")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.name
