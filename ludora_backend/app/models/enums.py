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
    AI_WORD_PROBLEM = "ai_word_problem" # New type for AI-generated word problems

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

class QuestStatus(str, Enum):
    """
    Defines the status of a quest.
    """
    PENDING = "pending"     # Quest has been generated but not yet started by the user (e.g. needs acceptance)
    ACTIVE = "active"       # Quest is currently in progress by the user
    COMPLETED = "completed"   # Quest has been successfully completed
    CANCELLED = "cancelled"   # Quest was cancelled or aborted
    # FAILED = "failed"     # Optional: If quests can be failed due to time limits or other conditions

class QuestObjectiveType(str, Enum):
    """
    Defines the types of objectives within a quest.
    """
    COMPLETE_QUIZ = "complete_quiz"                 # Target ID = Quiz ID (or a specific quiz configuration ID)
    COMPLETE_MINIGAME = "complete_minigame"           # Target ID = Minigame ID
    ANSWER_QUESTIONS_ON_TOPIC = "answer_questions_on_topic" # Target ID = Topic ID, Target Count = number of questions
    # ACHIEVE_SCORE_ON_QUIZ = "achieve_score_on_quiz"     # Target ID = Quiz ID, Target Count = minimum score
    # ACHIEVE_SCORE_ON_MINIGAME = "achieve_score_on_minigame" # Target ID = Minigame ID, Target Count = minimum score
    # SPEND_TIME_ON_TOPIC = "spend_time_on_topic"         # Target ID = Topic ID, Target Count = minutes spent
