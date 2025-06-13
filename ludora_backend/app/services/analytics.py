"""
Service for user performance analysis and recommendations.
"""
from typing import List, Dict, Set # Set is useful for unique topics

from ludora_backend.app.models.user import User
from ludora_backend.app.models.quiz import Quiz, QuizQuestionLink # QuizQuestionLink might not be directly needed if we use M2M accessor
from ludora_backend.app.models.question import Question # For type hinting if needed
from ludora_backend.app.models.topic import Topic # For type hinting

# LearningProgress model is not directly used in the refined logic,
# as we fetch Quizzes directly.

async def analyze_user_performance(user: User) -> List[Dict]:
    """
    Analyzes user's quiz performance to identify weak topics.
    Returns a list of dictionaries, each representing a weak topic and reasons.
    """
    topic_stats: Dict[int, Dict[str, any]] = {}
    # Key: topic_id, Value: {'total_score': float, 'attempts': int, 'topic_model': Topic}

    # Fetch quizzes completed by the user, along with questions and their topics.
    # The M2M accessor `quiz.questions` actually refers to the QuizQuestionLink instances.
    # To get to the Topic, we need: Quiz -> QuizQuestionLink -> Question -> Topic.
    user_quizzes = await Quiz.filter(user_id=user.id, completed_at__isnull=False, score__isnull=False).prefetch_related(
        'questions__question__topic' # Prefetches: QuizQuestionLink -> Question -> Topic
    )

    for quiz in user_quizzes:
        if quiz.score is None: # Should be filtered by query, but as a safeguard
            continue

        quiz_topics_for_this_quiz: Set[Topic] = set()
        for qql_entry in quiz.questions: # quiz.questions is the list of QuizQuestionLink instances
            if qql_entry.question and qql_entry.question.topic:
                # qql_entry.question is the Question model instance
                # qql_entry.question.topic is the Topic model instance
                quiz_topics_for_this_quiz.add(qql_entry.question.topic)

        # If a quiz covered multiple topics, its score contributes to each of those topics.
        for topic_model in quiz_topics_for_this_quiz:
            if topic_model.id not in topic_stats:
                topic_stats[topic_model.id] = {
                    'total_score': 0.0,
                    'attempts': 0,
                    'topic_model': topic_model # Store the Topic model instance
                }

            topic_stats[topic_model.id]['total_score'] += quiz.score
            topic_stats[topic_model.id]['attempts'] += 1

    weak_topic_data = []
    for topic_id, data in topic_stats.items():
        if data['attempts'] == 0: # Should not happen if quiz_score contributed
            continue

        average_score = data['total_score'] / data['attempts']

        # Define criteria for "weakness"
        # Example: Average score < 60% and at least 2 attempts on quizzes covering this topic.
        if average_score < 60.0 and data['attempts'] >= 1: # Changed to >=1 attempt for broader recommendations
            weak_topic_data.append({
                "topic_model": data['topic_model'], # Pass the actual Topic model instance
                "reason": "Average score below 60%.",
                "average_score": round(average_score, 2),
                "attempts": data['attempts']
            })

    return weak_topic_data
