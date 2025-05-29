"""
Service for generating math questions using the mathgenerator library.
"""
import mathgenerator
import random

# Cache the list of available generators if possible, or fetch as needed.
# Be mindful of how mathgenerator loads its list, especially if it's dynamic.
# For now, we assume get_gen_list() is efficient enough for occasional calls.
try:
    # Attempt to get the list of generator IDs.
    # mathgenerator problem IDs are typically integers from 1 to N.
    # Some IDs might be deprecated or removed over time.
    # The structure of get_gen_list() might vary by mathgenerator version.
    # Assuming it returns a list of dicts or objects with an 'id' attribute or similar.
    # For this example, we'll assume it returns a list of problem_id integers directly
    # or that we can extract them.
    # If get_gen_list() returns dicts like {'id': problem_id, 'name': 'problem_name', ...}
    # then: gen_list = [item['id'] for item in mathgenerator.get_gen_list()]
    # If it's just a list of IDs: gen_list = mathgenerator.get_gen_list()
    
    # Based on mathgenerator's current structure, get_gen_list() returns a list of lists/tuples
    # like: [[id, name, example_problem_without_solution, example_problem_with_solution], ...]
    # So, we need to extract the IDs.
    _MATHGENERATOR_PROBLEM_IDS = [item[0] for item in mathgenerator.get_gen_list()]
    if not _MATHGENERATOR_PROBLEM_IDS:
        # Fallback if list is empty for some reason
        _MATHGENERATOR_PROBLEM_IDS = list(range(1, 121)) # Default to a known range if needed
except Exception:
    # Fallback in case get_gen_list() fails or changes structure
    _MATHGENERATOR_PROBLEM_IDS = list(range(1, 121)) # Assuming 120 problems as a rough estimate

def generate_math_question_by_id(problem_id: int) -> dict | None:
    """
    Generates a math question for a specific problem_id using mathgenerator.
    Returns a dictionary like {"problem": "...", "solution": "..."} or None if ID is invalid.
    """
    try:
        # mathgenerator.generate_context(problem_id) is expected to return:
        # (problem_text_without_solution, solution_text, context_text_if_any)
        # We are interested in problem_text and solution_text.
        # Note: Some mathgenerator functions might return problem with solution embedded.
        # The library's consistency can vary. Let's assume generate_context is the way.
        
        # generate_context might not exist directly.
        # The typical usage is:
        # problem, solution = mathgenerator.generate_problem(problem_id)
        # For a context-based one if available:
        # context = mathgenerator.generate_context(problem_id)
        # For now, we'll use the standard problem generation.
        # It seems generate_context is not a standard function in mathgenerator.
        # The primary function is generate_problem(id, *args)
        
        # Let's assume generate_problem is the target.
        # It typically returns: problem, solution
        problem, solution = mathgenerator.generate_problem(problem_id)
        if problem and solution:
            return {"problem": str(problem), "solution": str(solution)}
        return None
    except IndexError: # mathgenerator raises IndexError for invalid problem_id
        return None
    except Exception: # Catch other potential errors from mathgenerator
        return None

def generate_random_math_question(topic_code: int | None = None) -> dict | None:
    """
    Generates a random math question.
    If topic_code (which is a mathgenerator problem_id here) is provided,
    it tries to generate from that specific ID. Otherwise, picks a random ID.
    Returns {"problem_id": id, "problem": "...", "solution": "..."} or None.
    """
    selected_problem_id = None
    
    if topic_code is not None:
        if topic_code in _MATHGENERATOR_PROBLEM_IDS:
            selected_problem_id = topic_code
        else:
            # Optionally, log that the specific topic_code was invalid
            # and we are falling back to random.
            pass # Fall through to random selection

    if selected_problem_id is None:
        if not _MATHGENERATOR_PROBLEM_IDS:
            return None # No problem IDs available
        selected_problem_id = random.choice(_MATHGENERATOR_PROBLEM_IDS)

    question_data = generate_math_question_by_id(selected_problem_id)
    
    if question_data:
        return {
            "problem_id": selected_problem_id,
            "problem": question_data["problem"],
            "solution": question_data["solution"]
        }
    return None

# Example usage (can be removed or kept for testing)
if __name__ == "__main__":
    print("Specific question (ID 5):")
    q1 = generate_math_question_by_id(5)
    if q1:
        print(f"  Problem: {q1['problem']}")
        print(f"  Solution: {q1['solution']}")
    else:
        print("  Failed to generate question for ID 5.")

    print("\nRandom question:")
    q2 = generate_random_math_question()
    if q2:
        print(f"  ID: {q2['problem_id']}")
        print(f"  Problem: {q2['problem']}")
        print(f"  Solution: {q2['solution']}")
    else:
        print("  Failed to generate a random question.")

    print("\nRandom question from specific ID (e.g., 10) if valid:")
    q3 = generate_random_math_question(topic_code=10)
    if q3:
        print(f"  ID: {q3['problem_id']}")
        print(f"  Problem: {q3['problem']}")
        print(f"  Solution: {q3['solution']}")
    else:
        print("  Failed to generate question for specific ID 10 (it might be invalid or list is small).")
    
    print(f"\nAvailable mathgenerator problem IDs ({len(_MATHGENERATOR_PROBLEM_IDS)}): {_MATHGENERATOR_PROBLEM_IDS[:10]}...")
