"""
Quiz endpoints for Ludora backend.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timezone # Ensure timezone is imported
import random # For random selection

from tortoise.transactions import atomic
from tortoise.expressions import Q # For OR queries

from ludora_backend.app.models.user import User
from ludora_backend.app.models.topic import Topic
from ludora_backend.app.models.question import Question
from ludora_backend.app.models.quiz import Quiz, QuizQuestionLink
from ludora_backend.app.models.progress import LearningProgress
from ludora_backend.app.schemas.quiz import QuizRead, QuizCreateRequest, QuizSubmit
# from ludora_backend.app.schemas.question import QuestionRead # Not directly used in type hints here
from ludora_backend.app.api.dependencies import get_current_active_user
from ludora_backend.app.services.question_generator import generate_random_math_question
from ludora_backend.app.models.enums import QuestionType

router = APIRouter()

@router.post("/quizzes/generate", response_model=QuizRead)
@atomic()
async def generate_quiz(
    quiz_params: QuizCreateRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Generates a new quiz for the currently authenticated user based on specified criteria.
    """
    db_quiz = await Quiz.create(user=current_user, name=quiz_params.name)
    selected_question_ids = set() # To keep track of questions already added to avoid duplicates
    final_selected_questions_for_quiz = [] # Store the actual Question objects

    for _ in range(quiz_params.num_questions): # Iterate for the number of questions needed
        current_slot_question: Optional[Question] = None
        
        # Build query for existing questions, excluding already selected ones
        query_filters = []
        if selected_question_ids: # Exclude already picked questions
            query_filters.append(~Q(id__in=list(selected_question_ids)))
        if quiz_params.topic_ids:
            query_filters.append(Q(topic_id__in=quiz_params.topic_ids))
        if quiz_params.difficulties:
            query_filters.append(Q(difficulty_level__in=quiz_params.difficulties))
        
        valid_question_types_enums = []
        if quiz_params.question_types:
            for qt_str in quiz_params.question_types:
                try:
                    valid_question_types_enums.append(QuestionType(qt_str))
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Invalid question type: {qt_str}")
            if valid_question_types_enums:
                query_filters.append(Q(question_type__in=valid_question_types_enums))

        # Attempt to fetch from existing questions first
        if query_filters: # Only query if there are some filters (beyond excluding selected)
            # Fetch more than 1 to allow random choice if multiple match
            potential_questions = await Question.filter(*query_filters).limit(10) 
            if potential_questions:
                current_slot_question = random.choice(potential_questions)

        # If no existing question found by criteria, or if MATH_GENERATOR is explicitly allowed/default
        if not current_slot_question and (
            not valid_question_types_enums or QuestionType.MATH_GENERATOR in valid_question_types_enums
        ):
            mathgen_topic_code = None
            topic_id_for_mathgen = None
            if quiz_params.topic_ids:
                # Prefer topics that are explicitly linked to mathgenerator IDs
                candidate_topics = await Topic.filter(id__in=quiz_params.topic_ids, mathgenerator_topic_ids__isnull=False).first()
                if candidate_topics and candidate_topics.mathgenerator_topic_ids:
                    mathgen_topic_code = random.choice(candidate_topics.mathgenerator_topic_ids)
                    topic_id_for_mathgen = candidate_topics.id
            
            q_data = generate_random_math_question(topic_code=mathgen_topic_code)
            if q_data:
                # Check if this generated question already exists to avoid near duplicates from mathgen
                # (e.g. same problem_id and text, but maybe different stored difficulty)
                existing_q = await Question.get_or_none(
                    mathgenerator_problem_id=q_data["problem_id"],
                    question_text=q_data["problem"],
                    id__not_in=list(selected_question_ids) # Ensure it's not one we've already picked
                )
                if existing_q:
                    current_slot_question = existing_q
                else:
                    # Create new question from mathgenerator
                    difficulty_for_mathgen = random.choice(quiz_params.difficulties) if quiz_params.difficulties else random.randint(1,3)
                    current_slot_question = await Question.create(
                        question_text=q_data["problem"],
                        answer_text=q_data["solution"],
                        question_type=QuestionType.MATH_GENERATOR,
                        mathgenerator_problem_id=q_data["problem_id"],
                        difficulty_level=difficulty_for_mathgen,
                        topic_id=topic_id_for_mathgen # Link to topic if mathgen ID came from it
                    )
        
        if not current_slot_question:
            # If after all attempts, no suitable unique question is found for this slot
            raise HTTPException(status_code=400, detail=f"Could not find or generate a unique question for slot {len(final_selected_questions_for_quiz) + 1} based on the criteria. Try broader criteria.")

        selected_question_ids.add(current_slot_question.id)
        final_selected_questions_for_quiz.append(current_slot_question)

    # Create all QuizQuestionLink entries
    for i, question_obj in enumerate(final_selected_questions_for_quiz):
        await QuizQuestionLink.create(quiz=db_quiz, question=question_obj, order=i)

    # Fetch the full quiz with questions and their details for the response
    await db_quiz.fetch_related('question_links__question', 'question_links__question__topic')
    return db_quiz


@router.get("/quizzes/{quiz_id}", response_model=QuizRead)
async def get_quiz(quiz_id: int, current_user: User = Depends(get_current_active_user)):
    """
    Retrieves a specific quiz by its ID for the currently authenticated user.
    """
    quiz = await Quiz.get_or_none(id=quiz_id, user_id=current_user.id) # Ensure user owns it
    if not quiz:
        # Check if quiz exists at all to give a more specific error
        if await Quiz.exists(id=quiz_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this quiz")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    
    # Efficiently fetch related data for the response model
    # QuizRead -> questions: List[QuizQuestionLinkRead]
    # QuizQuestionLinkRead -> question: QuestionRead
    # QuestionRead -> topic: Optional[TopicRead]
    await quiz.fetch_related('question_links__question__topic')
    return quiz

@router.post("/quizzes/{quiz_id}/submit", response_model=QuizRead)
@atomic()
async def submit_quiz(
    quiz_id: int,
    submission_data: QuizSubmit,
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits answers for a quiz, calculates the score, and marks the quiz as completed.
    """
    quiz = await Quiz.get_or_none(id=quiz_id, user_id=current_user.id)
    if not quiz:
        if await Quiz.exists(id=quiz_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to submit this quiz")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    
    if quiz.completed_at:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz already completed")

    # Fetch all question links for this quiz along with their actual questions
    quiz_links = await QuizQuestionLink.filter(quiz_id=quiz.id).prefetch_related('question')
    
    if not quiz_links:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Quiz has no questions associated with it.")

    total_questions_in_quiz = len(quiz_links)
    correct_answers_count = 0
    
    submitted_answers_map = {ans.question_id: ans.answer for ans in submission_data.answers}

    for qql in quiz_links:
        question_model = qql.question # This is the Question model instance
        user_answer_str = submitted_answers_map.get(question_model.id)

        if user_answer_str is not None:
            # Basic answer comparison (case-insensitive, strips whitespace)
            is_correct = (question_model.answer_text.strip().lower() == user_answer_str.strip().lower())
            
            qql.user_answer = user_answer_str
            qql.is_correct = is_correct
            await qql.save()

            if is_correct:
                correct_answers_count += 1
        else:
            # Question was not answered by the user
            qql.user_answer = None
            qql.is_correct = False
            await qql.save()


    quiz.score = (correct_answers_count / total_questions_in_quiz) * 100 if total_questions_in_quiz > 0 else 0
    quiz.completed_at = datetime.now(timezone.utc)
    await quiz.save()

    main_topic_id_for_progress = None
    if quiz_links and quiz_links[0].question and quiz_links[0].question.topic_id:
        main_topic_id_for_progress = str(quiz_links[0].question.topic_id)

    await LearningProgress.create(
        user=current_user,
        quiz_id=str(quiz.id),
        score=quiz.score,
        topic_id=main_topic_id_for_progress,
        completed_at=quiz.completed_at
    )

    await quiz.fetch_related('question_links__question__topic')
    return quiz
