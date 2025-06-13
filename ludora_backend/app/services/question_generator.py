"""
Service for generating math questions using the mathgenerator library.
"""
import mathgenerator
import random
from typing import Optional, List, Dict, Any # Added type hints

from ludora_backend.app.models.enums import QuestionType
from ludora_backend.app.models.question import Question
from ludora_backend.app.models.topic import Topic
from ludora_backend.app.schemas.ai_models import WordProblemInput
from ludora_backend.app.services.ai_models.word_problem_generator import generate_ai_word_problem

# Cache for mathgenerator problem IDs
_MATHGENERATOR_PROBLEM_IDS: List[int] = []
try:
    # Corrected based on previous findings: mathgenerator.getGenList()
    if hasattr(mathgenerator, 'getGenList'):
        problem_list_from_lib = mathgenerator.getGenList()
        if problem_list_from_lib:
            _MATHGENERATOR_PROBLEM_IDS = [item[0] for item in problem_list_from_lib if isinstance(item, (list, tuple)) and len(item) > 0]
    if not _MATHGENERATOR_PROBLEM_IDS and hasattr(mathgenerator, 'get_gen_list'): # Fallback
        problem_list_from_lib = mathgenerator.get_gen_list()
        if problem_list_from_lib:
             _MATHGENERATOR_PROBLEM_IDS = [item[0] for item in problem_list_from_lib if isinstance(item, (list, tuple)) and len(item) > 0]
    if not _MATHGENERATOR_PROBLEM_IDS:
        print("Warning: Could not populate _MATHGENERATOR_PROBLEM_IDS from library. Using fallback range.")
        _MATHGENERATOR_PROBLEM_IDS = list(range(0, 126)) # Based on observed output (0-125)
except Exception as e:
    print(f"Warning: Error initializing mathgenerator problem IDs: {e}. Using fallback range.")
    _MATHGENERATOR_PROBLEM_IDS = list(range(0, 126))


def _generate_math_question_from_mathgenerator_id(problem_id: int) -> Optional[Dict[str, str]]:
    """
    Generates a math question for a specific problem_id using mathgenerator.
    Returns a dictionary like {"problem": "...", "solution": "..."} or None if ID is invalid.
    Uses genById as per previous findings.
    """
    try:
        if hasattr(mathgenerator, 'genById'):
            problem, solution = mathgenerator.genById(problem_id)
            if problem and solution:
                return {"problem": str(problem), "solution": str(solution)}
        else: # Fallback for older assumption, though genById is more likely correct
             problem, solution = mathgenerator.generate_problem(problem_id) # type: ignore
             if problem and solution:
                return {"problem": str(problem), "solution": str(solution)}
        return None
    except IndexError:
        print(f"Info: mathgenerator problem_id {problem_id} not found (IndexError).")
        return None
    except Exception as e:
        print(f"Error generating math_question for id {problem_id}: {e}")
        return None

async def get_or_create_question_from_mathgenerator(
    mathgen_problem_id: Optional[int] = None,
    topic_id_for_new_question: Optional[int] = None,
    difficulty_for_new_question: Optional[int] = None
) -> Optional[Question]:
    """
    Fetches an existing question by mathgenerator_problem_id or generates a new one.
    If generated, it's saved to the database.
    """
    selected_problem_id = mathgen_problem_id

    if selected_problem_id is None: # Pick a random one if no specific ID is given
        if not _MATHGENERATOR_PROBLEM_IDS:
            print("Error: _MATHGENERATOR_PROBLEM_IDS is empty. Cannot select random math problem.")
            return None
        selected_problem_id = random.choice(_MATHGENERATOR_PROBLEM_IDS)

    # Try to find an existing question with this mathgenerator ID first (if one was determined)
    if selected_problem_id is not None:
        existing_question = await Question.filter(mathgenerator_problem_id=selected_problem_id).first()
        if existing_question:
            await existing_question.fetch_related('topic')
            return existing_question

    # If no specific ID or no existing question, generate, save, and return
    if selected_problem_id is not None:
        generated_data = _generate_math_question_from_mathgenerator_id(selected_problem_id)
        if generated_data:
            # Check again if this text combination already exists to avoid near-duplicates
            # if somehow the mathgenerator_problem_id wasn't unique enough or not set previously
            existing_by_text = await Question.filter(
                question_text=generated_data["problem"],
                answer_text=generated_data["solution"],
                question_type=QuestionType.MATH_GENERATOR
            ).first()
            if existing_by_text:
                 await existing_by_text.fetch_related('topic')
                 return existing_by_text

            new_question = await Question.create(
                topic_id=topic_id_for_new_question,
                difficulty_level=difficulty_for_new_question or random.randint(1, 3),
                question_text=generated_data["problem"],
                answer_text=generated_data["solution"],
                question_type=QuestionType.MATH_GENERATOR,
                mathgenerator_problem_id=selected_problem_id,
            )
            await new_question.fetch_related('topic')
            return new_question
    return None


async def get_or_create_question_from_ai_word_problem(
    topic_id: int, # Topic context is important for word problems
    difficulty_level: int,
    keywords: Optional[List[str]] = None
) -> Optional[Question]:
    """
    Generates a word problem using AI, saves it, and returns it.
    """
    topic = await Topic.get_or_none(id=topic_id)
    if not topic:
        print(f"Error: Topic with ID {topic_id} not found for AI word problem generation.")
        return None

    wp_input = WordProblemInput(
        topic=topic.name, # Use topic name for prompt context
        keywords=keywords or [], # Pass keywords if any
        # prompt_prefix: can be customized, e.g. based on difficulty
        # max_length: can be customized
    )

    ai_response = await generate_ai_word_problem(wp_input)

    if "Error:" in ai_response.generated_problem_text or not ai_response.generated_problem_text.strip():
        print(f"AI word problem generation failed or returned empty: {ai_response.generated_problem_text}")
        return None

    # Check for duplicates by text if desired, though AI generation aims for novelty
    # existing_question = await Question.filter(question_text=ai_response.generated_problem_text, question_type=QuestionType.AI_WORD_PROBLEM).first()
    # if existing_question:
    #    await existing_question.fetch_related('topic')
    #    return existing_question

    new_question = await Question.create(
        topic_id=topic_id,
        difficulty_level=difficulty_level,
        question_text=ai_response.generated_problem_text,
        answer_text="Answer to be determined by user or future AI step.", # Placeholder answer
        question_type=QuestionType.AI_WORD_PROBLEM,
    )
    await new_question.fetch_related('topic')
    return new_question
