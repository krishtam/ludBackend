"""
Pydantic schemas for Quizzes.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Assuming QuestionRead is in a sibling file 'question.py' within the same 'schemas' directory
from .question import QuestionRead 

class QuizQuestionLinkRead(BaseModel):
    """
    Schema for reading the link between a Quiz and a Question,
    including user's answer and correctness, and the full question details.
    """
    question_id: int # From the Question model via the link table
    order: int
    user_answer: Optional[str] = None
    is_correct: Optional[bool] = None
    question: QuestionRead # Nested full question details

    class Config:
        orm_mode = True

class QuizBase(BaseModel):
    """
    Base schema for a Quiz.
    """
    name: str = "Generated Quiz"

class QuizCreateRequest(BaseModel): # Renamed from QuizCreate to avoid conflict if QuizCreate is used elsewhere with different fields
    """
    Schema for requesting a new Quiz generation.
    """
    name: str = "Generated Quiz"
    num_questions: int = Field(10, gt=0, le=50)
    topic_ids: Optional[List[int]] = None
    difficulties: Optional[List[int]] = None
    # Ensure QuestionType is imported if not already
    # from ludora_backend.app.models.enums import QuestionType # Already done by QuestionRead import usually
    question_types: Optional[List[str]] = None # Using str for simplicity, can map to QuestionType in endpoint

class QuizRead(QuizBase):
    """
    Schema for reading Quiz data, including its questions and user progress.
    """
    id: int
    user_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    questions: List[QuizQuestionLinkRead] # Shows questions with their order and answers

    class Config:
        orm_mode = True

class QuizSubmissionAnswer(BaseModel):
    """
    Schema for a single answer submitted by a user for a question in a quiz.
    """
    question_id: int
    answer: str # User's submitted answer for this question

class QuizSubmit(BaseModel):
    """
    Schema for submitting all answers for a quiz.
    """
    answers: List[QuizSubmissionAnswer]
