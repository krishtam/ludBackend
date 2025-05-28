"""
Inventory endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends
from typing import List

from ludora_backend.app.models.user import User
from ludora_backend.app.models.inventory import InventoryItem
from ludora_backend.app.schemas.shop import InventoryItemRead # InventoryItemRead is in shop.py
from ludora_backend.app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=List[InventoryItemRead])
async def get_my_inventory(current_user: User = Depends(get_current_active_user)):
    """
    Retrieves all inventory items for the currently authenticated user.
    Item details are pre-fetched.
    """
    # Using user_id for filtering is more direct for database queries.
    # prefetch_related('item') ensures that the related Item model is fetched
    # in a single additional query, making it efficient for lists.
    inventory_items = await InventoryItem.filter(user_id=current_user.id).prefetch_related('item')
    return inventory_items
