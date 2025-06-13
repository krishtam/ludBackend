"""
Pydantic schemas for Shop and Inventory.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any # List is already imported in Python 3.9+ by default, but explicit is fine.

from ludora_backend.app.models.enums import ItemType

# Item Schemas
class ItemBase(BaseModel):
    """
    Base schema for Item.
    """
    name: str
    description: Optional[str] = None
    price: int
    item_type: ItemType
    # Pydantic field 'metadata' will map to model's 'metadata_' field.
    # Tortoise's JSONField typically returns a dict, so this should work.
    # If Tortoise returns a string, we might need a validator.
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")


class ItemCreate(ItemBase):
    """
    Schema for creating an Item.
    """
    pass

class ItemRead(ItemBase):
    """
    Schema for reading Item data.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# Paginated Response Schema for Items
class PaginatedItemRead(BaseModel):
    total: int = Field(..., description="Total number of items available.")
    items: List[ItemRead] = Field(..., description="List of items for the current page.")
    page: int = Field(..., description="Current page number.")
    size: int = Field(..., description="Number of items per page.")
    # Optional: Can add pages (total_pages) if needed
    # pages: Optional[int] = Field(None, description="Total number of pages.")
        # If 'metadata_' from the model is used, and we want 'metadata' in the schema output,
        # Pydantic v2 prefers using alias in the field definition itself (as done in ItemBase)
        # or using `alias_generator` in Config if there's a systematic transformation.
        # The `alias="metadata_"` in ItemBase's `metadata` field should handle mapping
        # from `Item.metadata_` to `ItemRead.metadata` during ORM to Pydantic conversion.
        # No need for `fields` attribute here if alias is correctly set in ItemBase.


# Inventory Schemas
class InventoryItemBase(BaseModel):
    """
    Base schema for InventoryItem.
    """
    item_id: int # We'll expect the item_id for creation/base representation
    quantity: int

class InventoryItemRead(InventoryItemBase):
    """
    Schema for reading InventoryItem data.
    Includes nested ItemRead for item details.
    """
    id: int
    user_id: int
    acquired_at: datetime
    used_at: Optional[datetime] = None
    item: ItemRead # To nest item details

    class Config:
        orm_mode = True

class InventoryItemUpdate(BaseModel):
    """
    Schema for updating an InventoryItem.
    """
    quantity: Optional[int] = None


# Purchase Schemas
class PurchaseCreate(BaseModel):
    """
    Schema for creating a Purchase.
    item_id will be taken from the path parameter.
    """
    quantity: int = Field(..., gt=0)

class PurchaseRead(BaseModel):
    """
    Schema for reading Purchase data.
    Includes nested ItemRead for item details.
    """
    id: int
    user_id: int
    # item_id: int # Redundant if 'item' (ItemRead) is included and contains the id. Kept for explicitness if needed.
    quantity: int
    total_price: int
    purchased_at: datetime
    item: ItemRead # To nest item details

    class Config:
        orm_mode = True
