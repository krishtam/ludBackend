"""
Quiz and QuizQuestionLink models for Ludora backend.
"""
from tortoise.models import Model
from tortoise import fields

class Quiz(Model):
    """
    Quiz model.
    """
    id = fields.IntField(pk=True, generated=True)
    user = fields.ForeignKeyField('models.User', related_name='quizzes', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=200, default="Generated Quiz")
    created_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    score = fields.FloatField(null=True)
    questions = fields.ManyToManyField(
        'models.Question', 
        through='quizquestionlink', 
        related_name='quizzes',
        # Specify custom on_delete for the M2M relationship if needed,
        # though CASCADE is typical for the link table's FKs.
        # The default for M2M fields themselves doesn't directly use on_delete in the same way.
    )

    def __str__(self):
        return f"{self.name} (User: {self.user_id})"

class QuizQuestionLink(Model):
    """
    Through model for Quiz and Question ManyToMany relationship.
    Stores details about each question within a specific quiz attempt.
    """
    quiz = fields.ForeignKeyField('models.Quiz', on_delete=fields.CASCADE, related_name='question_links')
    question = fields.ForeignKeyField('models.Question', on_delete=fields.CASCADE, related_name='quiz_links')
    order = fields.IntField(description="Order of question in the quiz")
    user_answer = fields.TextField(null=True)
    is_correct = fields.BooleanField(null=True)

    class Meta:
        table = "quiz_question_link" # Explicitly define table name
        unique_together = (("quiz", "question"), ("quiz", "order")) # Ensures a question appears once per quiz and order is unique within a quiz.

    def __str__(self):
        return f"Quiz {self.quiz_id} - Q {self.question_id} (Order: {self.order})"
