"""
Enum definitions for Ludora models.
"""
from enum import Enum

class ItemType(str, Enum):
    """
    Defines the types of items available in the shop.
    """
    POWER_UP = "power_up"
    THEME = "theme"
    TICKET = "ticket"
    CONSUMABLE = "consumable"
    COLLECTIBLE = "collectible"
