"""
Shop endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

from tortoise.transactions import atomic

from ludora_backend.app.models.user import User
from ludora_backend.app.models.profile import UserProfile
from ludora_backend.app.models.item import Item
from ludora_backend.app.models.inventory import InventoryItem
from ludora_backend.app.models.purchase import Purchase
from ludora_backend.app.schemas.shop import ItemRead, PurchaseCreate, PurchaseRead
from ludora_backend.app.api.dependencies import get_current_active_user

router = APIRouter()

@router.get("/items", response_model=List[ItemRead])
async def list_shop_items():
    """
    Lists all items available in the shop.
    """
    return await Item.all()

@router.post("/items/{item_id}/purchase", response_model=PurchaseRead)
@atomic() # Ensures all database operations within are part of a single transaction
async def purchase_item(
    item_id: int,
    purchase_data: PurchaseCreate,
    current_user: User = Depends(get_current_active_user)
):
    """
    Purchases an item from the shop for the currently authenticated user.
    """
    item_to_purchase = await Item.get_or_none(id=item_id)
    if not item_to_purchase:
        raise HTTPException(status_code=404, detail="Item not found")

    # UserProfile should exist due to the post_save signal on User creation.
    # Using .get() will raise an exception if not found, which is desired here
    # as it indicates a system inconsistency if a profile is missing for an active user.
    user_profile = await UserProfile.get(user_id=current_user.id)

    total_cost = item_to_purchase.price * purchase_data.quantity

    if user_profile.in_app_currency < total_cost:
        raise HTTPException(status_code=400, detail="Not enough currency")

    # Deduct currency
    user_profile.in_app_currency -= total_cost
    await user_profile.save()

    # Add/update inventory
    inventory_item = await InventoryItem.get_or_none(user=current_user, item=item_to_purchase)
    if inventory_item:
        inventory_item.quantity += purchase_data.quantity
    else:
        inventory_item = await InventoryItem.create(
            user=current_user, 
            item=item_to_purchase, 
            quantity=purchase_data.quantity
        )
    # inventory_item.save() is called implicitly by .create() or explicitly if updated.
    # If only quantity is updated, save() is needed.
    await inventory_item.save()


    # Record purchase
    new_purchase = await Purchase.create(
        user=current_user,
        item=item_to_purchase,
        quantity=purchase_data.quantity,
        total_price=total_cost
    )
    
    # For PurchaseRead to correctly serialize the nested ItemRead,
    # the 'item' field needs to be populated on the new_purchase instance.
    # Tortoise ORM typically requires an explicit fetch for related objects
    # if they weren't loaded during the initial query or creation.
    # Since 'item_to_purchase' is already the full Item object,
    # we can assign it directly if Tortoise doesn't automatically populate it
    # from the foreign key assignment during .create().
    # However, Tortoise is quite good. Let's test if fetch_related is needed.
    # It's safer to ensure the related field is loaded for the response model.
    await new_purchase.fetch_related('item') 
    
    return new_purchase
