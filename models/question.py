"""
Question Data Model for Quiz Application
Represents quiz questions with multiple choice answers.
"""

from typing import List, Dict, Optional, Any
from enum import Enum
import random


class DifficultyType(Enum):
    """Enumeration for question difficulty types."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


class Question:
    """Represents a single quiz question with multiple choice answers."""

    def __init__(self, question_text: str = "", options: List[str] = None,
                 correct_answer: str = "", marks: int = 1, difficulty: DifficultyType = DifficultyType.SIMPLE,
                 question_id: Optional[int] = None):
        """
        Initialize Question object.

        Args:
            question_text: The question text
            options: List of answer options (should contain 4 options)
            correct_answer: The correct answer option
            marks: Marks awarded for correct answer
            difficulty: Difficulty level of the question
            question_id: Database ID for the question
        """
        self.question_id = question_id
        self.question_text = question_text.strip()
        self.options = options.copy() if options else []
        self.correct_answer = correct_answer.strip()
        self.marks = marks
        self.difficulty = difficulty

        # Ensure we have exactly 4 options
        while len(self.options) < 4:
            self.options.append("")
        self.options = self.options[:4]

    @property
    def option1(self) -> str:
        """Get first option."""
        return self.options[0] if len(self.options) > 0 else ""

    @property
    def option2(self) -> str:
        """Get second option."""
        return self.options[1] if len(self.options) > 1 else ""

    @property
    def option3(self) -> str:
        """Get third option."""
        return self.options[2] if len(self.options) > 2 else ""

    @property
    def option4(self) -> str:
        """Get fourth option."""
        return self.options[3] if len(self.options) > 3 else ""

    def get_option(self, index: int) -> str:
        """
        Get option by index.

        Args:
            index: Option index (0-3)

        Returns:
            Option text or empty string if invalid index
        """
        if 0 <= index < len(self.options):
            return self.options[index]
        return ""

    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate question data.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Validate question text
        if not self.question_text:
            errors.append("Question text is required")
        elif len(self.question_text) < 5:
            errors.append("Question text must be at least 5 characters long")
        elif len(self.question_text) > 1000:
            errors.append("Question text cannot exceed 1000 characters")

        # Validate options
        valid_options = []
        for i, option in enumerate(self.options, 1):
            if not option.strip():
                errors.append(f"Option {i} is required")
            elif len(option.strip()) > 200:
                errors.append(f"Option {i} cannot exceed 200 characters")
            else:
                valid_options.append(option.strip())

        # Check for duplicate options
        if len(set(valid_options)) != len(valid_options):
            errors.append("All options must be unique")

        # Validate correct answer
        if not self.correct_answer:
            errors.append("Correct answer is required")
        elif self.correct_answer not in valid_options:
            errors.append("Correct answer must be one of the options")

        # Validate marks
        if not isinstance(self.marks, int) or self.marks <= 0:
            errors.append("Marks must be a positive integer")
        elif self.marks > 10:
            errors.append("Marks cannot exceed 10")

        # Validate difficulty
        if self.difficulty not in DifficultyType:
            errors.append("Invalid difficulty type")

        # Validate marks based on difficulty
        expected_marks = {
            DifficultyType.SIMPLE: 1,
            DifficultyType.MEDIUM: 2,
            DifficultyType.COMPLEX: 3
        }

        if self.difficulty in expected_marks and self.marks != expected_marks[self.difficulty]:
            errors.append(f"{self.difficulty.value} questions should be worth {expected_marks[self.difficulty]} marks")

        return len(errors) == 0, errors

    def check_answer(self, user_answer: str) -> bool:
        """
        Check if the user's answer is correct.

        Args:
            user_answer: User's selected answer

        Returns:
            True if answer is correct, False otherwise
        """
        return user_answer.strip() == self.correct_answer

    def shuffle_options(self, maintain_correct: bool = True) -> None:
        """
        Shuffle the options while optionally maintaining the correct answer position.

        Args:
            maintain_correct: If True, keeps track of the new correct answer position
        """
        if len(self.options) < 2:
            return

        # Store the original correct answer
        original_correct = self.correct_answer

        # Shuffle options
        random.shuffle(self.options)

        # Update correct answer if we need to maintain it
        if maintain_correct:
            self.correct_answer = original_correct
        else:
            # Find the new position of the original correct answer
            for option in self.options:
                if option == original_correct:
                    self.correct_answer = option
                    break

    def get_options_with_labels(self) -> Dict[str, str]:
        """
        Get options with alphabet labels (A, B, C, D).

        Returns:
            Dictionary mapping labels to option texts
        """
        labels = ['A', 'B', 'C', 'D']
        return {labels[i]: self.options[i] for i in range(min(4, len(self.options)))}

    def get_correct_option_label(self) -> str:
        """
        Get the label of the correct option.

        Returns:
            Label ('A', 'B', 'C', 'D') of correct option, or empty string if not found
        """
        for i, option in enumerate(self.options):
            if option == self.correct_answer:
                return ['A', 'B', 'C', 'D'][i]
        return ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert question object to dictionary.

        Returns:
            Dictionary representation of question
        """
        return {
            'question_id': self.question_id,
            'question_text': self.question_text,
            'options': self.options,
            'correct_answer': self.correct_answer,
            'marks': self.marks,
            'difficulty': self.difficulty.value if isinstance(self.difficulty, DifficultyType) else self.difficulty,
            'option1': self.option1,
            'option2': self.option2,
            'option3': self.option3,
            'option4': self.option4,
            'correct_option_label': self.get_correct_option_label()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Question':
        """
        Create question object from dictionary.

        Args:
            data: Dictionary containing question data

        Returns:
            Question object
        """
        # Handle difficulty
        difficulty = data.get('difficulty', DifficultyType.SIMPLE)
        if isinstance(difficulty, str):
            try:
                difficulty = DifficultyType(difficulty)
            except ValueError:
                difficulty = DifficultyType.SIMPLE

        # Handle options - try multiple formats
        options = []
        if 'options' in data and isinstance(data['options'], list):
            options = data['options']
        else:
            # Try individual option fields
            for i in range(1, 5):
                option_key = f'option{i}'
                if option_key in data:
                    options.append(data[option_key])

        return cls(
            question_text=data.get('question_text', ''),
            options=options,
            correct_answer=data.get('correct_answer', ''),
            marks=data.get('marks', 1),
            difficulty=difficulty,
            question_id=data.get('question_id')
        )

    @classmethod
    def from_database_row(cls, row) -> 'Question':
        """
        Create question object from database row.

        Args:
            row: Database row tuple

        Returns:
            Question object
        """
        if len(row) >= 9:
            difficulty_str = row[8]
            try:
                difficulty = DifficultyType(difficulty_str)
            except ValueError:
                difficulty = DifficultyType.SIMPLE

            options = [row[2], row[3], row[4], row[5]]  # option1, option2, option3, option4

            return cls(
                question_id=row[0],
                question_text=row[1],
                options=options,
                correct_answer=row[6],
                marks=row[7],
                difficulty=difficulty
            )
        else:
            raise ValueError("Invalid database row format for Question")

    def __str__(self) -> str:
        """String representation of question."""
        return f"Question({self.question_text[:50]}..., {self.difficulty.value}, {self.marks} marks)"

    def __repr__(self) -> str:
        """Detailed string representation of question."""
        return (f"Question(id={self.question_id}, text='{self.question_text[:30]}...', "
                f"difficulty={self.difficulty.value}, marks={self.marks})")

    def __eq__(self, other) -> bool:
        """Check equality with another question object."""
        if not isinstance(other, Question):
            return False
        return (self.question_text == other.question_text and
                self.options == other.options and
                self.correct_answer == other.correct_answer and
                self.marks == other.marks and
                self.difficulty == other.difficulty)

    def __hash__(self) -> int:
        """Generate hash for question object."""
        return hash((self.question_text, tuple(self.options), self.correct_answer, self.marks, self.difficulty))


class QuestionBank:
    """Manages a collection of questions."""

    def __init__(self):
        """Initialize question bank."""
        self.questions: List[Question] = []

    def add_question(self, question: Question) -> None:
        """
        Add a question to the bank.

        Args:
            question: Question to add
        """
        # Validate question before adding
        is_valid, errors = question.validate()
        if not is_valid:
            raise ValueError(f"Invalid question: {', '.join(errors)}")
        self.questions.append(question)

    def add_questions(self, questions: List[Question]) -> None:
        """
        Add multiple questions to the bank.

        Args:
            questions: List of questions to add
        """
        for question in questions:
            self.add_question(question)

    def get_questions_by_difficulty(self, difficulty: DifficultyType) -> List[Question]:
        """
        Get all questions of a specific difficulty.

        Args:
            difficulty: Difficulty type to filter by

        Returns:
            List of questions of specified difficulty
        """
        return [q for q in self.questions if q.difficulty == difficulty]

    def get_random_questions(self, count: int, difficulty: Optional[DifficultyType] = None) -> List[Question]:
        """
        Get random questions from the bank.

        Args:
            count: Number of questions to return
            difficulty: Optional difficulty filter

        Returns:
            List of random questions
        """
        available_questions = self.questions
        if difficulty:
            available_questions = self.get_questions_by_difficulty(difficulty)

        if count >= len(available_questions):
            return available_questions.copy()

        return random.sample(available_questions, count)

    def get_balanced_quiz(self, simple_count: int = 4, medium_count: int = 3, complex_count: int = 3) -> List[Question]:
        """
        Get a balanced set of questions for a quiz.

        Args:
            simple_count: Number of simple questions
            medium_count: Number of medium questions
            complex_count: Number of complex questions

        Returns:
            List of questions for the quiz
        """
        quiz_questions = []

        # Add simple questions
        simple_questions = self.get_random_questions(simple_count, DifficultyType.SIMPLE)
        quiz_questions.extend(simple_questions)

        # Add medium questions
        medium_questions = self.get_random_questions(medium_count, DifficultyType.MEDIUM)
        quiz_questions.extend(medium_questions)

        # Add complex questions
        complex_questions = self.get_random_questions(complex_count, DifficultyType.COMPLEX)
        quiz_questions.extend(complex_questions)

        # Shuffle the final quiz questions
        random.shuffle(quiz_questions)

        return quiz_questions

    def get_total_questions(self) -> int:
        """
        Get total number of questions in the bank.

        Returns:
            Total number of questions
        """
        return len(self.questions)

    def get_question_count_by_difficulty(self) -> Dict[str, int]:
        """
        Get count of questions by difficulty.

        Returns:
            Dictionary mapping difficulty to count
        """
        counts = {}
        for difficulty in DifficultyType:
            counts[difficulty.value] = len(self.get_questions_by_difficulty(difficulty))
        return counts

    def clear(self) -> None:
        """Clear all questions from the bank."""
        self.questions.clear()

    def to_dict_list(self) -> List[Dict[str, Any]]:
        """
        Convert all questions to list of dictionaries.

        Returns:
            List of question dictionaries
        """
        return [question.to_dict() for question in self.questions]

    @classmethod
    def from_dict_list(cls, data_list: List[Dict[str, Any]]) -> 'QuestionBank':
        """
        Create question bank from list of dictionaries.

        Args:
            data_list: List of question dictionaries

        Returns:
            QuestionBank object
        """
        bank = cls()
        for data in data_list:
            try:
                question = Question.from_dict(data)
                bank.add_question(question)
            except ValueError as e:
                # Skip invalid questions
                print(f"Skipping invalid question: {e}")
        return bank