"""
Leaderboard related models for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields
from .enums import ScoreType, Timeframe # Relative import

class Leaderboard(Model):
    """
    Represents a specific leaderboard, e.g., "Daily Quiz Overall".
    """
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=200, unique=True, description="e.g., Daily Quiz Overall, Weekly Minigame X High Score")
    score_type = fields.CharEnumField(ScoreType, max_length=50) # Max length to accommodate enum value strings
    timeframe = fields.CharEnumField(Timeframe, max_length=50) # Max length
    minigame = fields.ForeignKeyField(
        'models.Minigame', 
        null=True, 
        on_delete=fields.CASCADE, # Or SET_NULL if leaderboard should persist if minigame is deleted
        description="Link to minigame if score_type is minigame-specific"
    )
    topic = fields.ForeignKeyField(
        'models.Topic', 
        null=True, 
        on_delete=fields.CASCADE, # Or SET_NULL
        description="Link to topic if score_type is topic-specific"
    )
    last_updated = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    def __str__(self):
        return self.name

class LeaderboardEntry(Model):
    """
    Represents an entry in a leaderboard.
    """
    id = fields.IntField(pk=True, generated=True)
    leaderboard = fields.ForeignKeyField('models.Leaderboard', related_name='entries', on_delete=fields.CASCADE)
    user = fields.ForeignKeyField('models.User', related_name='leaderboard_entries', on_delete=fields.CASCADE)
    score = fields.FloatField()
    rank = fields.IntField(null=True, description="Calculated rank, can be updated periodically")
    # entry_date is meant to signify the period this entry is for.
    # For ALL_TIME, this might be less relevant or just the date of last update.
    # For DAILY, it's the specific day. For WEEKLY/MONTHLY, it could be the start date of the period.
    entry_date = fields.DateField(description="Date this entry pertains to (e.g., day for daily, start of week/month)")
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        # If entry_date is the specific day for daily leaderboards, then this unique_together is fine.
        # For weekly/monthly, if entry_date is the start_of_period, it's also fine.
        # For ALL_TIME, if entry_date is not consistently used or set to a fixed value (e.g., user join date),
        # then this might not be what you want. An ALL_TIME leaderboard might only have one entry per user.
        # Consider if ALL_TIME leaderboards should have a different structure or handling for entry_date.
        # For now, this structure implies an entry can be updated daily for a user on a given board.
        # If an ALL_TIME board means one single score ever, then (leaderboard, user) should be unique.
        # Let's assume for now that entry_date helps distinguish periods for periodic leaderboards,
        # and for ALL_TIME, it might be set to a fixed date or the date of the last score update.
        unique_together = (("leaderboard", "user", "entry_date"),)

    def __str__(self):
        return f"{self.user_id} on {self.leaderboard_id}: {self.score} (Rank: {self.rank})"
