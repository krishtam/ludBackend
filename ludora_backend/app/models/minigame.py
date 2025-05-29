"""
Minigame related models for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class Minigame(Model):
    """
    Minigame model.
    """
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=150, unique=True)
    description = fields.TextField(null=True)
    topic_focus = fields.ForeignKeyField(
        'models.Topic', 
        related_name='minigames', 
        on_delete=fields.SET_NULL, 
        null=True, 
        description="Primary topic this minigame focuses on"
    )
    question_count_per_session = fields.IntField(default=10, description="Default number of questions per minigame session")
    # Using metadata_ as the model field name, and "metadata" as the DB column name
    metadata_ = fields.JSONField(null=True, name="metadata", description="Game-specific settings or rules")

    def __str__(self):
        return self.name

class MinigameProgress(Model):
    """
    MinigameProgress model.
    Stores the outcome of a user's minigame session.
    """
    id = fields.IntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='minigame_sessions', on_delete=fields.CASCADE)
    minigame = fields.ForeignKeyField('models.Minigame', related_name='sessions', on_delete=fields.CASCADE)
    score = fields.IntField()
    currency_earned = fields.IntField(default=0)
    tickets_used = fields.IntField(default=0) # Example: if minigames can consume tickets
    powerups_applied = fields.JSONField(null=True, description="List of powerups used, e.g., [{'item_id': 1, 'type': 'skip_question'}]")
    session_duration_seconds = fields.IntField(null=True)
    completed_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"Session for {self.user_id} on {self.minigame_id} - Score: {self.score}"
