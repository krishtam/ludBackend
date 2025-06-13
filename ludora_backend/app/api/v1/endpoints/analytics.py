"""
User Analytics and Recommendations endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends
from typing import List # List is already imported in Python 3.9+ by default

from ludora_backend.app.models.user import User
from ludora_backend.app.api.dependencies import get_current_active_user
from ludora_backend.app.services.analytics import analyze_user_performance
from ludora_backend.app.schemas.analytics import RecommendationResponse, RecommendedTopic
from ludora_backend.app.schemas.question import TopicRead # For converting Topic model to TopicRead schema

router = APIRouter()

@router.get("/users/me/recommendations", response_model=RecommendationResponse)
async def get_user_recommendations(
    current_user: User = Depends(get_current_active_user)
):
    """
    Provides personalized recommendations based on user's performance analysis.
    """
    weak_topic_analysis_results = await analyze_user_performance(current_user)

    recommended_topics_response: List[RecommendedTopic] = []
    for result in weak_topic_analysis_results:
        # The 'topic_model' key from analyze_user_performance holds the Topic ORM instance.
        # We need to convert this to the TopicRead Pydantic schema.
        # Pydantic's from_orm (or model_validate for Pydantic v2 if directly from dict)
        # can be used if the ORM model is compatible. TopicRead.from_tortoise_orm may not exist.
        # Standard Pydantic v2 way from an ORM model instance: TopicRead.model_validate(result['topic_model'])
        # Or, if TopicRead is set up with orm_mode=True (Config.from_attributes=True for Pydantic V2)
        # it can often be done with TopicRead(**result['topic_model'].__dict__) but this is not robust.
        # The safest is usually `TopicRead.model_validate(orm_instance)` for Pydantic v2 or `TopicRead.from_orm(orm_instance)` for Pydantic v1.
        # Tortoise ORM models are Pydantic-compatible, so this should work.

        topic_orm_instance = result['topic_model'] # Renamed from 'topic' to 'topic_model' in analytics service
        topic_read_schema = TopicRead.model_validate(topic_orm_instance) # Pydantic v2
        # For Pydantic v1, it would be: topic_read_schema = TopicRead.from_orm(topic_orm_instance)


        recommended_topics_response.append(
            RecommendedTopic(
                topic=topic_read_schema,
                reason=result['reason'],
                average_score=result['average_score'],
                attempts=result['attempts']
            )
        )

    # Placeholder for suggested quizzes - can be enhanced later
    suggested_quizzes_list = []
    if recommended_topics_response:
        # Example: Suggest a generic quiz for the top weak topic
        top_weak_topic_name = recommended_topics_response[0].topic.name
        suggested_quizzes_list.append(f"Try a quiz on '{top_weak_topic_name}' to improve!")

    return RecommendationResponse(
        weak_topics=recommended_topics_response,
        suggested_quizzes=suggested_quizzes_list
    )
