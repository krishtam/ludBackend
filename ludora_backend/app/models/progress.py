"""
LearningProgress model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class LearningProgress(Model):
    """
    LearningProgress model.
    """
    id = fields.IntField(pk=True, generated=True) # Clarified generated=True as per common practice for pk IntFields
    user = fields.ForeignKeyField('models.User', related_name='progress_records', on_delete=fields.CASCADE)
    module_id = fields.CharField(max_length=100, null=True, description="Identifier for a learning module")
    quiz_id = fields.CharField(max_length=100, null=True, description="Identifier for a quiz taken")
    minigame_id = fields.CharField(max_length=100, null=True, description="Identifier for a minigame played")
    topic_id = fields.CharField(max_length=100, null=True, description="Identifier for the topic")
    subtopic_id = fields.CharField(max_length=100, null=True, description="Identifier for the subtopic")
    score = fields.IntField(null=True, description="Score obtained, if applicable")
    completed_at = fields.DatetimeField(auto_now_add=True, description="Timestamp of completion or attempt")
    progress_percentage = fields.FloatField(null=True, description="Percentage completion if it's a module")
    metadata = fields.JSONField(null=True, description="Any other relevant data, e.g., answers given")

    def __str__(self):
        # Similar to UserProfile, accessing user_id directly might require the user object to be fetched.
        # return f"Progress for User ID: {self.user_id} - Module: {self.module_id or 'N/A'}, Quiz: {self.quiz_id or 'N/A'}"
        user_id_str = str(self.user_id) if hasattr(self, 'user_id') else 'N/A'
        return f"Progress for User ID: {user_id_str} - Module: {self.module_id or 'N/A'}, Quiz: {self.quiz_id or 'N/A'}"
