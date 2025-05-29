"""
Pydantic schemas for User Analytics and Recommendations.
"""
from pydantic import BaseModel
from typing import List, Optional # List is already imported in Python 3.9+ by default

from ludora_backend.app.schemas.question import TopicRead # Assuming TopicRead is available

class RecommendedTopic(BaseModel):
    """
    Schema for a recommended topic based on performance analysis.
    """
    topic: TopicRead
    reason: str
    average_score: Optional[float] = None
    attempts: Optional[int] = None

    class Config:
        orm_mode = True # Useful if we ever construct this from an ORM model directly

class RecommendationResponse(BaseModel):
    """
    Schema for the overall recommendation response.
    """
    weak_topics: List[RecommendedTopic]
    suggested_quizzes: List[str] # Placeholder for now
