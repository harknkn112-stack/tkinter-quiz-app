"""
Sample Questions Data for Quiz Application
Contains predefined questions for testing and initial database population.
"""

# Sample questions distributed by difficulty level
SAMPLE_QUESTIONS = {
    "simple": [
        {
            "question": "What is 10 + 20?",
            "option1": "10",
            "option2": "20",
            "option3": "30",
            "option4": "40",
            "correct": "30",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "What is the capital of France?",
            "option1": "London",
            "option2": "Berlin",
            "option3": "Paris",
            "option4": "Madrid",
            "correct": "Paris",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "Which planet is closest to the Sun?",
            "option1": "Venus",
            "option2": "Mercury",
            "option3": "Earth",
            "option4": "Mars",
            "correct": "Mercury",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "What color do you get when mixing red and white?",
            "option1": "Pink",
            "option2": "Purple",
            "option3": "Orange",
            "option4": "Brown",
            "correct": "Pink",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "How many days are there in a week?",
            "option1": "5",
            "option2": "6",
            "option3": "7",
            "option4": "8",
            "correct": "7",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "What is 2 × 2?",
            "option1": "2",
            "option2": "4",
            "option3": "6",
            "option4": "8",
            "correct": "4",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "Which animal is known as the 'King of the Jungle'?",
            "option1": "Tiger",
            "option2": "Elephant",
            "option3": "Lion",
            "option4": "Bear",
            "correct": "Lion",
            "marks": 1,
            "type": "simple"
        },
        {
            "question": "What is the largest planet in our solar system?",
            "option1": "Earth",
            "option2": "Mars",
            "option3": "Jupiter",
            "option4": "Saturn",
            "correct": "Jupiter",
            "marks": 1,
            "type": "simple"
        }
    ],
    "medium": [
        {
            "question": "What is the square root of 144?",
            "option1": "10",
            "option2": "11",
            "option3": "12",
            "option4": "13",
            "correct": "12",
            "marks": 2,
            "type": "medium"
        },
        {
            "question": "Who painted the Mona Lisa?",
            "option1": "Vincent van Gogh",
            "option2": "Leonardo da Vinci",
            "option3": "Pablo Picasso",
            "option4": "Rembrandt",
            "correct": "Leonardo da Vinci",
            "marks": 2,
            "type": "medium"
        },
        {
            "question": "What is the chemical symbol for gold?",
            "option1": "Go",
            "option2": "Gd",
            "option3": "Au",
            "option4": "Ag",
            "correct": "Au",
            "marks": 2,
            "type": "medium"
        },
        {
            "question": "In which year did World War I begin?",
            "option1": "1912",
            "option2": "1914",
            "option3": "1916",
            "option4": "1918",
            "correct": "1914",
            "marks": 2,
            "type": "medium"
        },
        {
            "question": "What is the capital of Australia?",
            "option1": "Sydney",
            "option2": "Melbourne",
            "option3": "Canberra",
            "option4": "Perth",
            "correct": "Canberra",
            "marks": 2,
            "type": "medium"
        },
        {
            "question": "Who wrote 'Romeo and Juliet'?",
            "option1": "Charles Dickens",
            "option2": "William Shakespeare",
            "option3": "Jane Austen",
            "option4": "Mark Twain",
            "correct": "William Shakespeare",
            "marks": 2,
            "type": "medium"
        }
    ],
    "complex": [
        {
            "question": "What is the derivative of x² + 3x + 2?",
            "option1": "2x + 3",
            "option2": "x + 3",
            "option3": "2x² + 3x",
            "option4": "x² + 3",
            "correct": "2x + 3",
            "marks": 3,
            "type": "complex"
        },
        {
            "question": "In which year did World War II end?",
            "option1": "1943",
            "option2": "1944",
            "option3": "1945",
            "option4": "1946",
            "correct": "1945",
            "marks": 3,
            "type": "complex"
        },
        {
            "question": "What is the binary representation of decimal 10?",
            "option1": "1010",
            "option2": "1001",
            "option3": "1100",
            "option4": "0110",
            "correct": "1010",
            "marks": 3,
            "type": "complex"
        },
        {
            "question": "What is the integral of 2x + 3?",
            "option1": "x² + 3x + C",
            "option2": "2x² + 3x + C",
            "option3": "x² + 3x² + C",
            "option4": "x² + 3",
            "correct": "x² + 3x + C",
            "marks": 3,
            "type": "complex"
        },
        {
            "question": "Which philosopher wrote 'The Republic'?",
            "option1": "Aristotle",
            "option2": "Plato",
            "option3": "Socrates",
            "option4": "Confucius",
            "correct": "Plato",
            "marks": 3,
            "type": "complex"
        }
    ]
}


def populate_database(db_manager) -> None:
    """
    Populate database with sample questions.

    Args:
        db_manager: DatabaseManager instance
    """
    try:
        cursor = db_manager.connection.cursor()

        # Insert simple questions
        for question in SAMPLE_QUESTIONS["simple"]:
            cursor.execute(
                """
                INSERT INTO Questions (question, option1, option2, option3, option4, correct, marks, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question["question"],
                    question["option1"],
                    question["option2"],
                    question["option3"],
                    question["option4"],
                    question["correct"],
                    question["marks"],
                    question["type"]
                )
            )

        # Insert medium questions
        for question in SAMPLE_QUESTIONS["medium"]:
            cursor.execute(
                """
                INSERT INTO Questions (question, option1, option2, option3, option4, correct, marks, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question["question"],
                    question["option1"],
                    question["option2"],
                    question["option3"],
                    question["option4"],
                    question["correct"],
                    question["marks"],
                    question["type"]
                )
            )

        # Insert complex questions
        for question in SAMPLE_QUESTIONS["complex"]:
            cursor.execute(
                """
                INSERT INTO Questions (question, option1, option2, option3, option4, correct, marks, type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    question["question"],
                    question["option1"],
                    question["option2"],
                    question["option3"],
                    question["option4"],
                    question["correct"],
                    question["marks"],
                    question["type"]
                )
            )

        db_manager.connection.commit()

    except Exception as e:
        db_manager.connection.rollback()
        raise Exception(f"Failed to populate database with sample questions: {e}")


def get_sample_questions() -> dict:
    """
    Get all sample questions.

    Returns:
        Dictionary containing questions by difficulty level
    """
    return SAMPLE_QUESTIONS


def validate_sample_data() -> bool:
    """
    Validate sample data structure and content.

    Returns:
        True if data is valid
    """
    required_types = ["simple", "medium", "complex"]
    required_fields = ["question", "option1", "option2", "option3", "option4", "correct", "marks", "type"]

    for q_type in required_types:
        if q_type not in SAMPLE_QUESTIONS:
            return False

        for question in SAMPLE_QUESTIONS[q_type]:
            for field in required_fields:
                if field not in question:
                    return False

            # Validate marks based on type
            if q_type == "simple" and question["marks"] != 1:
                return False
            elif q_type == "medium" and question["marks"] != 2:
                return False
            elif q_type == "complex" and question["marks"] != 3:
                return False

    return True