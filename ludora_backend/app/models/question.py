"""
Question model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields
from .enums import QuestionType # Relative import for enums

class Question(Model):
    """
    Question model.
    """
    id = fields.IntField(pk=True, generated=True)
    topic = fields.ForeignKeyField('models.Topic', related_name='questions', on_delete=fields.SET_NULL, null=True)
    difficulty_level = fields.IntField(default=1, description="1-5 scale")
    question_text = fields.TextField()
    answer_text = fields.TextField() # Could be JSON for multiple choice options, or just the direct answer for free text
    question_type = fields.CharEnumField(QuestionType, max_length=50)
    mathgenerator_problem_id = fields.IntField(null=True, description="If sourced from mathgenerator")
    custom_template_data = fields.JSONField(null=True, description="Data for template-based questions")
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __str__(self):
        return self.question_text[:50]
