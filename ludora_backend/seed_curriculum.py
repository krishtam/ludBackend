import asyncio
import json # json.dumps will be used for storing list of ints as JSON string in DB
from tortoise import Tortoise, run_async

# Imports assuming the script is run as a module from the parent directory of 'ludora_backend'
# or that 'ludora_backend' is in PYTHONPATH.
from ludora_backend.app.models.topic import Topic
from ludora_backend.app.core.db import TORTOISE_ORM_CONFIG as APP_DB_CONFIG
from ludora_backend.app.core.config import settings

# Comprehensive Curriculum Data using mathgenerator IDs 0-125
# This is a best-effort categorization.
CURRICULUM_DATA = [
    {
        "subject_name": "Elementary Math",
        "units": [
            {"unit_name": "Basic Operations", "description": "Fundamental arithmetic operations: addition, subtraction, multiplication, and division.", "math_ids": [0, 1, 2, 3, 5, 6, 8, 71]},
            {"unit_name": "Number Theory Basics", "description": "Introduction to number properties like LCM, GCD, factors, and prime numbers.", "math_ids": [9, 10, 27, 40, 51, 90, 116, 120, 124]},
            {"unit_name": "Fractions and Decimals", "description": "Understanding fractions, decimals, and conversions between them.", "math_ids": [13, 16, 28, 44]},
            {"unit_name": "Measurement & Time", "description": "Basic measurement concepts and time conversions.", "math_ids": [81, 102]},
            {"unit_name": "Basic Geometry Shapes", "description": "Introduction to perimeter and area of simple shapes.", "math_ids": [29, 32, 33, 35, 36, 58, 96, 104]},
        ]
    },
    {
        "subject_name": "Middle School Math / Pre-Algebra",
        "units": [
            {"unit_name": "Exponents and Roots", "description": "Working with exponents, powers, and square/cube roots.", "math_ids": [47, 53, 97, 98, 99]},
            {"unit_name": "Basic Algebra & Expressions", "description": "Introduction to algebraic expressions, variables, and simple equations.", "math_ids": [11, 26, 105, 111]},
            {"unit_name": "Ratios, Proportions, and Percentages", "description": "Understanding ratios, proportions, percentages, and their applications.", "math_ids": [45, 63, 80, 118, 119]},
            {"unit_name": "Data Analysis & Probability Basics", "description": "Introduction to mean, median, mode, and basic probability concepts.", "math_ids": [52, 59, 76, 107]},
            {"unit_name": "Coordinate Plane Basics", "description": "Introduction to the coordinate plane, points, and distances.", "math_ids": [20, 24]},
            {"unit_name": "Geometric Figures", "description": "Angles, triangles, quadrilaterals, and basic geometric theorems.", "math_ids": [18, 19, 22, 25, 49, 125]},
        ]
    },
    {
        "subject_name": "Algebra I",
        "units": [
            {"unit_name": "Solving Linear Equations", "description": "Solving single and multi-step linear equations.", "math_ids": [26]}, # Repeated, but fits here too
            {"unit_name": "Systems of Equations", "description": "Solving systems of linear equations in two variables.", "math_ids": [23, 41]},
            {"unit_name": "Polynomials & Factoring", "description": "Operations with polynomials and factoring techniques.", "math_ids": [21]}, # Factoring Quadratic
            {"unit_name": "Quadratic Equations", "description": "Solving quadratic equations using various methods.", "math_ids": [50, 100]},
            {"unit_name": "Inequalities", "description": "Solving and graphing linear inequalities.", "math_ids": []}, # No direct mathgenerator ID found
            {"unit_name": "Functions Introduction", "description": "Understanding functions, domain, range, and function notation.", "math_ids": [106]}, # Signum function as an example
        ]
    },
    {
        "subject_name": "Geometry",
        "units": [
            {"unit_name": "Lines and Angles", "description": "Properties of lines, angles, parallel lines, and transversals.", "math_ids": [125]}, # Complementary/Supplementary
            {"unit_name": "Triangles", "description": "Properties of triangles, congruence, similarity, and Pythagorean theorem.", "math_ids": [18, 19, 22, 25]}, # Repeated
            {"unit_name": "Quadrilaterals and Polygons", "description": "Properties of various quadrilaterals and polygons.", "math_ids": [29, 49, 58, 96]}, # Repeated
            {"unit_name": "Circles", "description": "Properties of circles, arcs, chords, tangents, and sectors.", "math_ids": [75, 104, 108, 112, 115]},
            {"unit_name": "Surface Area and Volume", "description": "Calculating surface area and volume of 3D shapes.", "math_ids": [32, 33, 34, 35, 36, 37, 38, 39, 60, 61, 95, 113, 117, 122, 123]},
            {"unit_name": "Transformations", "description": "Translations, rotations, reflections, and dilations.", "math_ids": []}, # No direct mathgenerator ID
        ]
    },
    {
        "subject_name": "Algebra II / Advanced Algebra",
        "units": [
            {"unit_name": "Advanced Polynomials", "description": "Factoring higher-degree polynomials, polynomial division, remainder theorem.", "math_ids": []}, # No specific ID
            {"unit_name": "Rational Expressions", "description": "Simplifying, adding, subtracting, multiplying, and dividing rational expressions.", "math_ids": []}, # No specific ID
            {"unit_name": "Logarithmic & Exponential Functions", "description": "Properties and graphs of logarithmic and exponential functions.", "math_ids": [12]}, # Logarithm
            {"unit_name": "Sequences and Series", "description": "Arithmetic and geometric sequences and series.", "math_ids": [56, 62, 66, 82, 83]},
            {"unit_name": "Matrices", "description": "Operations with matrices, determinants, and inverses.", "math_ids": [17, 46, 74, 77]},
            {"unit_name": "Complex Numbers", "description": "Operations with complex numbers, polar form.", "math_ids": [65, 92, 100]}, # Complex quadratic
        ]
    },
    {
        "subject_name": "Trigonometry & Precalculus",
        "units": [
            {"unit_name": "Trigonometric Functions", "description": "Definitions, graphs, and properties of trigonometric functions.", "math_ids": [57, 86, 87]},
            {"unit_name": "Vectors", "description": "Vector operations, dot product, cross product, and applications.", "math_ids": [43, 69, 70, 72]},
            {"unit_name": "Analytic Geometry", "description": "Conic sections, parametric equations, polar coordinates.", "math_ids": [92]}, # Complex to Polar
            {"unit_name": "Introduction to Calculus Concepts", "description": "Limits, basic differentiation rules.", "math_ids": [7, 48, 88, 89, 110]}, # Power rule diff/int, trig diff, definite int, stationary points
        ]
    },
    {
        "subject_name": "Computer Science Math",
        "units": [
            {"unit_name": "Number Systems", "description": "Binary, hexadecimal, octal, and BCD conversions.", "math_ids": [4, 14, 15, 64, 73, 79, 84, 91, 94, 103]},
            {"unit_name": "Set Theory", "description": "Basic set operations.", "math_ids": [93]},
        ]
    },
    {
        "subject_name": "Statistics & Probability",
        "units": [
            {"unit_name": "Descriptive Statistics", "description": "Mean, median, variance, standard deviation.", "math_ids": [59, 76]}, # Repeated
            {"unit_name": "Probability", "description": "Basic probability, conditional probability, distributions.", "math_ids": [52, 54, 107, 109]},
            {"unit_name": "Combinatorics", "description": "Permutations and combinations.", "math_ids": [30, 42]},
        ]
    },
     {
        "subject_name": "Miscellaneous Math",
        "units": [
            {"unit_name": "Financial Math", "description": "Simple and compound interest, profit/loss.", "math_ids": [45, 63, 78]},
            {"unit_name": "General Problem Solving", "description": "Miscellaneous problems and puzzles.", "math_ids": [55, 101, 121]} # Comparing surds, Leap year, Product of scientific notations
        ]
    }
]

async def seed_topics():
    """
    Seeds the database with topics from the CURRICULUM_DATA.
    Uses update_or_create to be idempotent.
    """
    print("Starting to seed curriculum data...")
    for subject_info in CURRICULUM_DATA:
        subject_name = subject_info["subject_name"]
        print(f"\nProcessing Subject: {subject_name}")
        for unit_info in subject_info["units"]:
            topic_name = unit_info["unit_name"]
            description = unit_info["description"]
            # math_ids are stored as a JSON string in the DB, but Topic model expects list of ints for this field
            # when creating/updating. Tortoise ORM handles the JSON conversion for JSONField.
            math_ids_list = unit_info["math_ids"]

            # Using update_or_create for idempotency
            # 'defaults' are applied only if a new record is created or if an existing one is found and needs updating with these values.
            # If the record exists and matches 'name' and 'subject', its 'description' and 'mathgenerator_topic_ids'
            # will be updated to the values in 'defaults'.
            topic, created = await Topic.update_or_create(
                name=topic_name,
                subject=subject_name, # Adding subject to the lookup keys to ensure uniqueness per subject
                defaults={
                    "description": description,
                    "mathgenerator_topic_ids": math_ids_list # Pass the list directly
                }
            )

            if created:
                print(f"  CREATED Topic: '{topic.name}' in Subject: '{topic.subject}'")
            else:
                print(f"  UPDATED Topic: '{topic.name}' in Subject: '{topic.subject}'")
    print("\nCurriculum data seeding finished.")

async def main():
    """
    Main function to initialize Tortoise and run the seeder.
    """
    print(f"Using Database URL: {settings.DATABASE_URL}")

    # Use the same model loading structure as the main app if possible,
    # ensuring all models involved (directly or via relations) are known.
    # For this script, primarily 'app.models.topic' and 'aerich.models' are essential.
    # The original APP_DB_CONFIG['apps']['models']['models'] contains all app models.

    DB_CONFIG_FOR_SEEDER = {
         "connections": {"default": settings.DATABASE_URL},
         "apps": {
             "models": {
                 "models": APP_DB_CONFIG["apps"]["models"]["models"], # Use all models from main app config
                 "default_connection": "default",
             },
         },
         "use_tz": False, # Consistent with conftest.py and default Tortoise behavior
    }

    await Tortoise.init(config=DB_CONFIG_FOR_SEEDER)
    # generate_schemas might be too aggressive if migrations are strictly managed by Aerich.
    # However, for a seeder script, ensuring the table exists can be useful,
    # especially if it's run in an environment where migrations might not have run yet.
    # If Aerich is the sole source of truth for schema, this might be omitted or conditional.
    # For a seeder script, it's often helpful to ensure schemas exist.
    await Tortoise.generate_schemas(safe=True) # safe=True won't drop existing tables/columns

    print("Database initialized for seeder and schemas ensured/generated.")

    await seed_topics()

    await Tortoise.close_connections()
    print("Database connections closed.")

if __name__ == "__main__":
    print("Running curriculum seeder...")
    run_async(main())
