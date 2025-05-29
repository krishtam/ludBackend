"""
Pydantic schemas for Topics and Questions.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any # List is already imported in Python 3.9+ by default

from ludora_backend.app.models.enums import QuestionType

# Topic Schemas
class TopicBase(BaseModel):
    name: str
    subject: str = "Math"
    description: Optional[str] = None
    mathgenerator_topic_ids: Optional[List[int]] = None

class TopicCreate(TopicBase):
    pass

class TopicRead(TopicBase):
    id: int

    class Config:
        orm_mode = True

# Question Schemas
class QuestionBase(BaseModel):
    topic_id: Optional[int] = None
    difficulty_level: int = Field(1, ge=1, le=5) # Add validation for difficulty
    question_text: str
    answer_text: str # This could be a JSON string for complex answers like multi-choice
    question_type: QuestionType
    mathgenerator_problem_id: Optional[int] = None
    custom_template_data: Optional[Dict[str, Any]] = None # Changed from dict | None to Optional[Dict[str, Any]]

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    topic: Optional[TopicRead] = None # Nested Topic information

    class Config:
        orm_mode = True
