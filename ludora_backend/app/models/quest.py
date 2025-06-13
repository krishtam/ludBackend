"""
Quest related models for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields
from .enums import QuestStatus, QuestObjectiveType # Relative import

class Quest(Model):
    """
    Represents a learning quest assigned to a user.
    """
    id = fields.IntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='quests', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=200, default="Learning Quest")
    description = fields.TextField(null=True)
    status = fields.CharEnumField(QuestStatus, default=QuestStatus.ACTIVE, max_length=50) # Ensure max_length accommodates enum values
    reward_currency = fields.IntField(default=0, description="Currency awarded upon quest completion")
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)

    # objectives: fields.ReverseRelation["QuestObjective"] # Defined by QuestObjective's ForeignKey

    def __str__(self):
        return f"Quest '{self.name}' for User {self.user_id} (Status: {self.status.value})"

class QuestObjective(Model):
    """
    Represents an individual objective within a quest.
    """
    id = fields.IntField(pk=True, generated=True)
    quest = fields.ForeignKeyField('models.Quest', related_name='objectives', on_delete=fields.CASCADE)
    objective_type = fields.CharEnumField(QuestObjectiveType, max_length=50) # Ensure max_length
    target_id = fields.CharField(max_length=100, null=True, description="ID of the quiz, minigame, or topic (can be string or int, stored as string for flexibility)")
    target_count = fields.IntField(default=1, description="e.g., number of questions to answer, times to complete a minigame")
    current_progress = fields.IntField(default=0)
    is_completed = fields.BooleanField(default=False)
    description_override = fields.TextField(null=True, description="Specific description for this objective if needed, overrides default generated one.")

    def __str__(self):
        return f"Objective for Quest {self.quest_id}: {self.objective_type.value} - Target: {self.target_id or 'N/A'} ({self.current_progress}/{self.target_count})"
