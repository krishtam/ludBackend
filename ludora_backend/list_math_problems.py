import mathgenerator
import json

def list_problems():
    """
    Fetches and prints the list of available math problems from the mathgenerator library.
    """
    problem_list = []
    try:
        # Based on dir(mathgenerator) output, getGenList seems to be the correct function name.
        if hasattr(mathgenerator, 'getGenList'):
            problem_list = mathgenerator.getGenList()
        elif hasattr(mathgenerator, 'get_gen_list'): # Fallback just in case
            problem_list = mathgenerator.get_gen_list()
        else:
            print("Could not find 'getGenList' or 'get_gen_list' in mathgenerator module.")
            print("Available attributes (public):")
            for name in dir(mathgenerator):
                if not name.startswith('_'):
                    print(f"  {name}")
            return

        if not problem_list:
            print("No problems found or the problem list function returned an empty list.")
            return

        print("Available Math Problems from mathgenerator:")
        print("==========================================")
        # The structure of items from getGenList() was previously assumed to be
        # a list of lists: [id, name, example_problem, example_solution]
        # Let's print based on this structure first, and add a raw print if it fails.
        for item_index, problem_details in enumerate(problem_list):
            try:
                if isinstance(problem_details, (list, tuple)) and len(problem_details) >= 2:
                    problem_id = problem_details[0]
                    problem_name = problem_details[1]
                    # Example: problem_details[2]
                    # Solution: problem_details[3]
                    print(f"ID: {problem_id}, Name: {problem_name}")
                else:
                    # If the format is different (e.g., dict or other), print raw for inspection
                    print(f"Entry {item_index} (raw format): {problem_details}")
            except Exception as e:
                print(f"Error processing entry {item_index} ('{problem_details}'): {e}")

        print("\n==========================================")
        print(f"Total problems found: {len(problem_list)}")

        # To help with curriculum design, also show how to generate a problem using genById
        if hasattr(mathgenerator, 'genById') and problem_list:
            print("\nExample of generating a problem using genById (e.g., ID of first problem):")
            try:
                first_problem_id = problem_list[0][0] # Assuming list of lists and first item is ID
                problem, solution = mathgenerator.genById(first_problem_id)
                print(f"  Generated for ID {first_problem_id}:")
                print(f"    Problem: {problem}")
                print(f"    Solution: {solution}")
            except Exception as e:
                print(f"  Could not generate example problem with genById: {e}")
        else:
            print("\n'genById' function not found or problem list is empty, cannot show generation example.")


    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure 'mathgenerator' is installed correctly and the API is as expected.")

if __name__ == "__main__":
    list_problems()
