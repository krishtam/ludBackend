from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class WeaknessPredictionInput(BaseModel):
    """
    Input features for the AI Weakness Prediction model.
    Represents aggregated user performance data.
    """
    average_score_per_topic: Dict[str, float] = Field(
        ...,
        example={"algebra_linear_equations": 0.65, "geometry_triangles": 0.50},
        description="Average scores per topic identifier (e.g., topic slug or ID)."
    )
    recent_quiz_scores: List[float] = Field(
        ...,
        example=[0.7, 0.55, 0.6],
        description="A list of the user's most recent quiz scores."
    )
    time_spent_per_topic_minutes: Dict[str, int] = Field(
        ...,
        example={"algebra_linear_equations": 120, "geometry_triangles": 90},
        description="Total time spent in minutes per topic identifier."
    )
    # Note: The actual features and their structure would be determined by the trained model.

class PredictedWeakness(BaseModel):
    """
    Details of a single predicted weakness for a user.
    """
    topic_id: str = Field(..., description="Identifier for the topic predicted as a weakness.", example="algebra_linear_equations")
    weakness_probability: float = Field(
        ...,
        ge=0.0, le=1.0,
        description="The model's confidence (probability) that this topic is a weakness.",
        example=0.85
    )
    suggested_action_level: int = Field(
        ...,
        ge=1, le=3,
        description="Suggested intervention level: 1 (Monitor), 2 (Suggest Practice), 3 (Recommend Intervention).",
        example=2
    )

class WeaknessPredictionOutput(BaseModel):
    """
    Output from the AI Weakness Prediction model, listing predicted weaknesses for a user.
    """
    user_id: str = Field(..., description="Identifier for the user for whom predictions are made.", example="user_abc_123")
    predicted_weaknesses: List[PredictedWeakness] = Field(..., description="A list of predicted weaknesses.")
    # overall_confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="An overall confidence score for the set of predictions.")


# Schemas for Word Problem Generation
class WordProblemInput(BaseModel):
    """
    Input parameters for generating an AI-powered word problem.
    """
    topic: str = Field(..., example="Basic Algebra", description="The educational topic for the word problem.")
    keywords: List[str] = Field(
        default_factory=list,
        example=["apples", "oranges", "total cost"],
        description="Optional keywords to guide the problem generation."
    )
    prompt_prefix: str = Field(
        "generate a word problem about: ",
        example="generate a word problem about: ",
        description="Prefix for the prompt sent to the T5 model."
    )
    max_length: int = Field(
        150, ge=50, le=300,
        description="Maximum desired length for the generated problem text."
    )

class WordProblemOutput(BaseModel):
    """
    Output from the AI Word Problem Generator.
    """
    generated_problem_text: str = Field(..., description="The AI-generated word problem.", example="If Sarah has 5 apples and buys 3 more, how many apples does she have in total?")
    # Optional: could include extracted entities, an auto-generated answer if model supports it, etc.


# Schemas for Paraphrasing
class ParaphraseInput(BaseModel):
    """
    Input for the AI Paraphrasing service.
    """
    text_to_paraphrase: str = Field(..., example="The quick brown fox jumps over the lazy dog.", description="The text content to be paraphrased.")
    simplification_level: int = Field(
        default=1, ge=1, le=3,
        example=1,
        description="Desired level of simplification: 1 (minor), 2 (moderate), 3 (major)."
    )
    max_length: int = Field(
        150, ge=20, le=500,
        description="Maximum desired length for the paraphrased text."
    )

class ParaphraseOutput(BaseModel):
    """
    Output from the AI Paraphrasing service.
    """
    original_text: str = Field(..., description="The original text submitted for paraphrasing.")
    paraphrased_text: str = Field(..., description="The generated paraphrase.", example="A fast, dark-colored fox leaps above a sleepy canine.")
    # Optional: confidence_score: float


# Schemas for "The Guide" AI Tutoring Agent
class ProblemState(BaseModel):
    """
    Represents the current state of the problem the user is working on with "The Guide".
    """
    question_id: str = Field(..., description="Identifier for the question being worked on.", example="q_algebra_101")
    current_problem_statement: str = Field(..., description="The text of the problem.", example="Solve for x: 2x + 3 = 7")
    # current_step: Optional[int] = Field(None, description="Current step in a multi-step problem, if applicable.")
    # previous_hints: List[str] = Field(default_factory=list, description="History of hints already provided for this attempt/state.")
    # internal_state_blob: Optional[Dict[str, Any]] = Field(None, description="JSON blob for the guide to maintain more complex state across interactions.")

class GuideInput(BaseModel):
    """
    Input from the user to "The Guide" AI agent.
    """
    problem_state: ProblemState = Field(..., description="The current state of the problem.")
    user_attempt: str = Field(..., description="The user's answer or solution attempt for the current problem/step.", example="x = 2")
    # user_id: Optional[str] = Field(None, description="Identifier for the user, if personalization is active.")

class GuideHint(BaseModel):
    """
    A single hint provided by "The Guide".
    """
    hint_text: str = Field(..., description="The text content of the hint.", example="Remember to isolate the variable 'x'.")
    hint_type: str = Field(
        "general",
        example="next_step",
        description="Type of hint (e.g., 'general', 'specific_error', 'next_step', 'clarification')."
    )

class GuideOutput(BaseModel):
    """
    Output from "The Guide" AI agent in response to a user's attempt.
    """
    feedback_correctness: str = Field(
        ...,
        example="partially_correct",
        description="Assessment of the user's attempt (e.g., 'correct', 'incorrect', 'partially_correct', 'unknown')."
    )
    feedback_message: Optional[str] = Field(None, description="A general feedback message for the user.", example="You're on the right track, but check your final calculation.")
    hints: List[GuideHint] = Field(default_factory=list, description="A list of hints to help the user proceed.")
    # request_clarification: bool = Field(False, description="True if the guide needs more information from the user to proceed.")
    # problem_completed: bool = Field(False, description="True if the guide assesses the problem as successfully completed.")
