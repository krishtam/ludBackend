"""
Question and Topic endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request # Added Request
from typing import List, Optional

from ludora_backend.app.core.limiter import limiter # Corrected import
from ludora_backend.app.models.user import User # For auth if needed, not strictly for now
from ludora_backend.app.models.topic import Topic
from ludora_backend.app.models.question import Question
from ludora_backend.app.schemas.question import QuestionRead, QuestionCreate, TopicRead, TopicCreate
# from ludora_backend.app.api.dependencies import get_current_active_user # Not used in this file currently
from ludora_backend.app.services.question_generator import (
    get_or_create_question_from_mathgenerator,
    get_or_create_question_from_ai_word_problem
)
from ludora_backend.app.models.enums import QuestionType
import random

router = APIRouter()

# Topic Endpoints (Admin/Helper)
# TODO: Protect this endpoint - should only be accessible by admin/superuser.
@router.post("/topics", response_model=TopicRead, tags=["Topics"])
# @limiter.limit("...") # Example: Add if admin endpoints also need limiting
async def create_topic(request: Request, topic_data: TopicCreate): # Add auth dependency (e.g. current_user: User = Depends(get_current_admin_user)))
    """
    Creates a new topic. (Admin/Helper endpoint)
    """
    # Check for existing topic by name
    if await Topic.exists(name=topic_data.name):
        raise HTTPException(status_code=400, detail=f"Topic with name '{topic_data.name}' already exists.")
    new_topic = await Topic.create(**topic_data.model_dump())
    return new_topic

@router.get("/topics", response_model=List[TopicRead], tags=["Topics"])
# @limiter.limit("...")
async def list_topics(request: Request): # Add auth dependency later if needed
    """
    Lists all topics. (Admin/Helper endpoint)
    """
    return await Topic.all()

# Question Endpoints
# TODO: Protect this endpoint - should only be accessible by admin/superuser.
@router.post("/questions", response_model=QuestionRead, tags=["Questions"])
# @limiter.limit("...")
async def create_custom_question(request: Request, question_data: QuestionCreate): # Add auth dependency (e.g. current_user: User = Depends(get_current_admin_user)))
    """
    Creates a new custom question. (Admin/Helper endpoint for custom questions)
    """
    # Ensure topic exists if topic_id is provided
    if question_data.topic_id and not await Topic.exists(id=question_data.topic_id):
        raise HTTPException(status_code=404, detail=f"Topic with id {question_data.topic_id} not found.")

    new_question = await Question.create(**question_data.model_dump())
    await new_question.fetch_related('topic') # Ensure topic is loaded for the response
    return new_question

@router.get("/questions/generate", response_model=QuestionRead, tags=["Questions"])
@limiter.limit("30/minute")
async def get_generated_question(
    request: Request, # Added Request parameter
    topic_id: Optional[int] = None,
    difficulty: Optional[int] = Query(None, ge=1, le=5), # Keep difficulty for future use
    question_type: QuestionType = Query(QuestionType.MATH_GENERATOR), # Default to MATH_GENERATOR
    # Add keywords for AI Word Problem, optional
    keywords: Optional[List[str]] = Query(None, description="Keywords for AI Word Problem generation")
):
    """
    Generates a question or fetches one based on criteria.
    Supports MATH_GENERATOR, AI_WORD_PROBLEM, and custom types.
    """
    question: Optional[Question] = None

    if question_type == QuestionType.MATH_GENERATOR:
        mathgen_problem_id_to_use: Optional[int] = None
        if topic_id:
            topic = await Topic.get_or_none(id=topic_id)
            if topic and topic.mathgenerator_topic_ids:
                valid_ids = [pid for pid in topic.mathgenerator_topic_ids if isinstance(pid, int)]
                if valid_ids:
                    mathgen_problem_id_to_use = random.choice(valid_ids)

        question = await get_or_create_question_from_mathgenerator(
            mathgen_problem_id=mathgen_problem_id_to_use,
            topic_id_for_new_question=topic_id,
            difficulty_for_new_question=difficulty
        )

    elif question_type == QuestionType.AI_WORD_PROBLEM:
        if not topic_id:
            raise HTTPException(status_code=400, detail="topic_id is required for AI_WORD_PROBLEM generation.")

        # Use provided difficulty or a default random one if not specified for AI questions.
        # This is consistent with how MATH_GENERATOR questions are handled in the service if difficulty isn't passed.
        difficulty_to_use = difficulty or random.randint(1, 3)

        question = await get_or_create_question_from_ai_word_problem(
            topic_id=topic_id,
            difficulty_level=difficulty_to_use,
            keywords=keywords or []
        )

    elif question_type == QuestionType.CUSTOM_TEMPLATE or question_type == QuestionType.CUSTOM_STATIC:
        query = Question.filter(question_type=question_type)
        if topic_id:
            query = query.filter(topic_id=topic_id)
        if difficulty:
            query = query.filter(difficulty_level=difficulty)

        # Fetch a random question matching criteria
        # .first() might not be random. For true random, other techniques are needed.
        # For now, this is a simplified fetch.
        custom_question = await query.order_by("?").first() # "ORDER BY RANDOM()" for SQLite/Postgres, "?": Tortoise specific
        if custom_question:
            await custom_question.fetch_related('topic')
            return custom_question
        # raise HTTPException(status_code=501, detail="Custom question types not fully implemented yet for dynamic fetching.")
        # Fall through to 404 if no custom question found matching criteria

    raise HTTPException(status_code=404, detail="No question found/generated for the criteria.")
