"""
Topic model for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class Topic(Model):
    """
    Topic model.
    """
    id = fields.IntField(pk=True, generated=True)
    name = fields.CharField(max_length=150, unique=True)
    subject = fields.CharField(max_length=100, default="Math")
    description = fields.TextField(null=True)
    mathgenerator_topic_ids = fields.JSONField(null=True, description="List of mathgenerator problem IDs relevant to this topic")

    def __str__(self):
        return self.name
