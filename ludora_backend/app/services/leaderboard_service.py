"""
Service layer for leaderboard logic.
"""
from typing import List
from datetime import datetime, date, timedelta # Ensure all are imported

from ludora_backend.app.models.leaderboard import Leaderboard, LeaderboardEntry
from ludora_backend.app.models.user import User # For type hinting if needed
from ludora_backend.app.models.quiz import Quiz # For update logic
from ludora_backend.app.models.minigame import MinigameProgress # For update logic
from ludora_backend.app.models.topic import Topic # For type hinting if needed
from ludora_backend.app.models.enums import ScoreType, Timeframe

async def get_leaderboard_entries(leaderboard_id: int, limit: int = 100) -> List[LeaderboardEntry]:
    """
    Fetches entries for a specific leaderboard, ordered by score descending, then by updated_at ascending.
    """
    return await LeaderboardEntry.filter(leaderboard_id=leaderboard_id).order_by('-score', 'updated_at').limit(limit).prefetch_related('user')

async def update_quiz_overall_leaderboard(leaderboard: Leaderboard):
    """
    Placeholder for actual calculation logic for quiz overall scores.
    This would query Quiz scores, aggregate them per user based on the leaderboard.timeframe,
    and update/create LeaderboardEntry records.
    """
    # Example: If it's a daily leaderboard, you'd filter quizzes completed today.
    # today = date.today()
    # start_datetime = datetime.combine(today, datetime.min.time())
    # end_datetime = datetime.combine(today, datetime.max.time())
    # if leaderboard.timeframe == Timeframe.DAILY:
    #     user_scores = await Quiz.filter(
    #         completed_at__gte=start_datetime,
    #         completed_at__lte=end_datetime
    #     ).group_by('user_id').annotate(average_score=Avg('score'), user_id_alias='user_id')
    #     # Process user_scores and update LeaderboardEntry...
    print(f"Placeholder: Would update QUIZ OVERALL leaderboard '{leaderboard.name}' for timeframe '{leaderboard.timeframe.value}'.")

async def update_minigame_high_score_leaderboard(leaderboard: Leaderboard):
    """
    Placeholder for actual calculation logic for minigame high scores.
    This would query MinigameProgress for the linked leaderboard.minigame_id,
    find highest scores per user based on the leaderboard.timeframe.
    """
    if not leaderboard.minigame_id:
        print(f"Error: Leaderboard '{leaderboard.name}' is for minigame high scores but no minigame is linked.")
        return
    # Example:
    # if leaderboard.timeframe == Timeframe.ALL_TIME:
    #     user_high_scores = await MinigameProgress.filter(
    #         minigame_id=leaderboard.minigame_id
    #     ).group_by('user_id').annotate(max_score=Max('score'), user_id_alias='user_id')
    #     # Process user_high_scores and update LeaderboardEntry...
    print(f"Placeholder: Would update MINIGAME HIGH SCORE leaderboard '{leaderboard.name}' for minigame ID {leaderboard.minigame_id} and timeframe '{leaderboard.timeframe.value}'.")

async def update_topic_proficiency_leaderboard(leaderboard: Leaderboard):
    """
    Placeholder for actual calculation logic for topic proficiency.
    """
    if not leaderboard.topic_id:
        print(f"Error: Leaderboard '{leaderboard.name}' is for topic proficiency but no topic is linked.")
        return
    print(f"Placeholder: Would update TOPIC PROFICIENCY leaderboard '{leaderboard.name}' for topic ID {leaderboard.topic_id} and timeframe '{leaderboard.timeframe.value}'.")

async def update_overall_xp_leaderboard(leaderboard: Leaderboard):
    """
    Placeholder for actual calculation logic for overall XP.
    """
    # This would likely involve summing XP from various sources (quizzes, minigames, etc.)
    print(f"Placeholder: Would update OVERALL XP leaderboard '{leaderboard.name}' for timeframe '{leaderboard.timeframe.value}'.")
