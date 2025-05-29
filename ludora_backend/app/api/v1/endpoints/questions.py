"""
Question and Topic endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from ludora_backend.app.models.user import User # For auth if needed, not strictly for now
from ludora_backend.app.models.topic import Topic
from ludora_backend.app.models.question import Question
from ludora_backend.app.schemas.question import QuestionRead, QuestionCreate, TopicRead, TopicCreate
from ludora_backend.app.api.dependencies import get_current_active_user # Optional for now
from ludora_backend.app.services.question_generator import generate_random_math_question, generate_math_question_by_id
from ludora_backend.app.models.enums import QuestionType
import random

router = APIRouter()

# Topic Endpoints (Admin/Helper)
@router.post("/topics", response_model=TopicRead, tags=["Topics"])
async def create_topic(topic_data: TopicCreate): # Add auth dependency later if needed
    """
    Creates a new topic. (Admin/Helper endpoint)
    """
    # Check for existing topic by name
    if await Topic.exists(name=topic_data.name):
        raise HTTPException(status_code=400, detail=f"Topic with name '{topic_data.name}' already exists.")
    new_topic = await Topic.create(**topic_data.model_dump())
    return new_topic

@router.get("/topics", response_model=List[TopicRead], tags=["Topics"])
async def list_topics(): # Add auth dependency later if needed
    """
    Lists all topics. (Admin/Helper endpoint)
    """
    return await Topic.all()

# Question Endpoints
@router.post("/questions", response_model=QuestionRead, tags=["Questions"])
async def create_custom_question(question_data: QuestionCreate): # Add auth dependency later if needed
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
async def get_generated_question(
    topic_id: Optional[int] = None,
    difficulty: Optional[int] = Query(None, ge=1, le=5), # Keep difficulty for future use
    question_type: QuestionType = Query(QuestionType.MATH_GENERATOR) # Default to MATH_GENERATOR
):
    """
    Generates a question or fetches one based on criteria.
    Primarily uses mathgenerator for now.
    """
    if question_type == QuestionType.MATH_GENERATOR:
        mathgen_problem_id = None
        if topic_id:
            topic = await Topic.get_or_none(id=topic_id)
            if topic and topic.mathgenerator_topic_ids:
                # Filter out any non-integer IDs from JSON, though they should be ints
                valid_ids = [pid for pid in topic.mathgenerator_topic_ids if isinstance(pid, int)]
                if valid_ids:
                    mathgen_problem_id = random.choice(valid_ids)
        
        # If specific topic ID didn't yield a mathgen_problem_id, or no topic_id was given
        if mathgen_problem_id is None:
            generated_q_data = generate_random_math_question()
        else:
            # Use the specific mathgen_problem_id if found from topic
            generated_q_data = generate_random_math_question(topic_code=mathgen_problem_id)

        if not generated_q_data:
            raise HTTPException(status_code=404, detail="Failed to generate math question from mathgenerator.")

        # Check if this question (by mathgenerator_problem_id and text) already exists to avoid duplicates
        existing_question = await Question.get_or_none(
            mathgenerator_problem_id=generated_q_data["problem_id"],
            question_text=generated_q_data["problem"]
        )

        if existing_question:
            await existing_question.fetch_related('topic')
            return existing_question

        # Create a new Question record
        # Guess difficulty if not provided, or use the provided one.
        # Assign topic if a specific topic_id led to this generation.
        question_create_data = {
            "topic_id": topic_id if mathgen_problem_id else None, # Link topic if it was used to select mathgen_id
            "difficulty_level": difficulty or random.randint(1, 3), # Default/random difficulty
            "question_text": generated_q_data["problem"],
            "answer_text": generated_q_data["solution"],
            "question_type": QuestionType.MATH_GENERATOR,
            "mathgenerator_problem_id": generated_q_data["problem_id"],
        }
        new_question = await Question.create(**question_create_data)
        await new_question.fetch_related('topic')
        return new_question

    elif question_type == QuestionType.CUSTOM_TEMPLATE or question_type == QuestionType.CUSTOM_STATIC:
        # Basic placeholder for custom questions
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
