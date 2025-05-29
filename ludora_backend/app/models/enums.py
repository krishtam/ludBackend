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

class ScoreType(str, Enum):
    """
    Defines the types of scores tracked on leaderboards.
    """
    QUIZ_OVERALL = "quiz_overall"
    MINIGAME_HIGH_SCORE = "minigame_high_score"
    OVERALL_XP = "overall_xp"
    TOPIC_PROFICIENCY = "topic_proficiency"

class Timeframe(str, Enum):
    """
    Defines the timeframes for leaderboards.
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"
