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

class QuestionType(str, Enum):
    """
    Defines the types of questions.
    """
    MATH_GENERATOR = "math_generator"
    CUSTOM_TEMPLATE = "custom_template" # For word problems with randomized variables
    CUSTOM_STATIC = "custom_static"   # Manually created, fixed questions
