"""
Student Data Model for Quiz Application
Represents student information and quiz results.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import re


class Student:
    """Represents a student taking the quiz."""

    def __init__(self, name: str = "", university: str = "", usn: Optional[int] = None,
                 date_of_exam: Optional[str] = None, marks_scored: int = 0):
        """
        Initialize Student object.

        Args:
            name: Student name
            university: University name
            usn: Unique Student Number (database ID)
            date_of_exam: Date and time of exam
            marks_scored: Total marks scored in quiz
        """
        self.name = name.strip()
        self.university = university.strip()
        self.usn = usn
        self.date_of_exam = date_of_exam
        self.marks_scored = marks_scored
        self.answers = []  # List to store selected answers
        self.quiz_start_time = None
        self.quiz_end_time = None

    @property
    def display_name(self) -> str:
        """
        Get formatted display name.

        Returns:
            Formatted student name
        """
        return self.name.title() if self.name else "Unknown Student"

    @property
    def display_university(self) -> str:
        """
        Get formatted university name.

        Returns:
            Formatted university name
        """
        return self.university.title() if self.university else "Unknown University"

    def validate_name(self, name: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate student name.

        Args:
            name: Name to validate (uses instance name if None)

        Returns:
            Tuple of (is_valid, error_message)
        """
        name_to_check = name if name is not None else self.name

        if not name_to_check:
            return False, "Name is required"

        name_to_check = name_to_check.strip()

        if not name_to_check:
            return False, "Name cannot be empty or whitespace only"

        if len(name_to_check) < 2:
            return False, "Name must be at least 2 characters long"

        if len(name_to_check) > 50:
            return False, "Name cannot exceed 50 characters"

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", name_to_check):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"

        return True, ""

    def validate_university(self, university: Optional[str] = None) -> tuple[bool, str]:
        """
        Validate university name.

        Args:
            university: University name to validate (uses instance university if None)

        Returns:
            Tuple of (is_valid, error_message)
        """
        university_to_check = university if university is not None else self.university

        if not university_to_check:
            return False, "University is required"

        university_to_check = university_to_check.strip()

        if not university_to_check:
            return False, "University cannot be empty or whitespace only"

        if len(university_to_check) < 2:
            return False, "University must be at least 2 characters long"

        if len(university_to_check) > 100:
            return False, "University cannot exceed 100 characters"

        # Check for valid characters (letters, numbers, spaces, common punctuation)
        if not re.match(r"^[a-zA-Z0-9\s\-\.,'\&]+$", university_to_check):
            return False, "University contains invalid characters"

        return True, ""

    def validate(self) -> tuple[bool, list]:
        """
        Validate all student data.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        name_valid, name_error = self.validate_name()
        if not name_valid:
            errors.append(name_error)

        university_valid, university_error = self.validate_university()
        if not university_valid:
            errors.append(university_error)

        return len(errors) == 0, errors

    def set_name(self, name: str) -> None:
        """
        Set student name after validation.

        Args:
            name: New student name

        Raises:
            ValueError: If name is invalid
        """
        is_valid, error = self.validate_name(name)
        if not is_valid:
            raise ValueError(error)
        self.name = name.strip()

    def set_university(self, university: str) -> None:
        """
        Set university name after validation.

        Args:
            university: New university name

        Raises:
            ValueError: If university is invalid
        """
        is_valid, error = self.validate_university(university)
        if not is_valid:
            raise ValueError(error)
        self.university = university.strip()

    def start_quiz(self) -> None:
        """Record quiz start time."""
        self.quiz_start_time = datetime.now()
        self.answers = []  # Reset answers for new quiz

    def end_quiz(self) -> None:
        """Record quiz end time."""
        self.quiz_end_time = datetime.now()

    def set_answers(self, answers: list) -> None:
        """
        Set the student's answers.

        Args:
            answers: List of selected answers (one per question)
        """
        self.answers = answers.copy()

    def get_answers(self) -> list:
        """
        Get the student's answers.

        Returns:
            List of selected answers
        """
        return self.answers.copy()

    def add_answer(self, question_number: int, answer: str) -> None:
        """
        Add or update answer for a specific question.

        Args:
            question_number: Question index (0-based)
            answer: Selected answer
        """
        # Ensure answers list is long enough
        while len(self.answers) <= question_number:
            self.answers.append("")

        self.answers[question_number] = answer

    def get_answer(self, question_number: int) -> str:
        """
        Get answer for a specific question.

        Args:
            question_number: Question index (0-based)

        Returns:
            Selected answer or empty string if not answered
        """
        if 0 <= question_number < len(self.answers):
            return self.answers[question_number]
        return ""

    def calculate_time_taken(self) -> int:
        """
        Calculate time taken for quiz in seconds.

        Returns:
            Time taken in seconds, or 0 if quiz not completed
        """
        if self.quiz_start_time and self.quiz_end_time:
            return int((self.quiz_end_time - self.quiz_start_time).total_seconds())
        return 0

    def get_formatted_time_taken(self) -> str:
        """
        Get formatted time taken string.

        Returns:
            Formatted time string (MM:SS) or "Not completed"
        """
        time_seconds = self.calculate_time_taken()
        if time_seconds == 0:
            return "Not completed"

        minutes = time_seconds // 60
        seconds = time_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert student object to dictionary.

        Returns:
            Dictionary representation of student
        """
        return {
            'usn': self.usn,
            'name': self.name,
            'university': self.university,
            'date_of_exam': self.date_of_exam,
            'marks_scored': self.marks_scored,
            'answers': self.answers,
            'quiz_start_time': self.quiz_start_time.isoformat() if self.quiz_start_time else None,
            'quiz_end_time': self.quiz_end_time.isoformat() if self.quiz_end_time else None,
            'time_taken': self.calculate_time_taken()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Student':
        """
        Create student object from dictionary.

        Args:
            data: Dictionary containing student data

        Returns:
            Student object
        """
        student = cls(
            name=data.get('name', ''),
            university=data.get('university', ''),
            usn=data.get('usn'),
            date_of_exam=data.get('date_of_exam'),
            marks_scored=data.get('marks_scored', 0)
        )

        if 'answers' in data:
            student.set_answers(data['answers'])

        if data.get('quiz_start_time'):
            student.quiz_start_time = datetime.fromisoformat(data['quiz_start_time'])

        if data.get('quiz_end_time'):
            student.quiz_end_time = datetime.fromisoformat(data['quiz_end_time'])

        return student

    @classmethod
    def from_database_row(cls, row) -> 'Student':
        """
        Create student object from database row.

        Args:
            row: Database row tuple

        Returns:
            Student object
        """
        if len(row) >= 5:
            return cls(
                usn=row[0],
                name=row[1],
                university=row[2],
                date_of_exam=row[3],
                marks_scored=row[4]
            )
        else:
            raise ValueError("Invalid database row format for Student")

    def __str__(self) -> str:
        """String representation of student."""
        return f"Student({self.name}, {self.university}, USN: {self.usn})"

    def __repr__(self) -> str:
        """Detailed string representation of student."""
        return (f"Student(usn={self.usn}, name='{self.name}', university='{self.university}', "
                f"marks_scored={self.marks_scored})")

    def __eq__(self, other) -> bool:
        """Check equality with another student object."""
        if not isinstance(other, Student):
            return False
        return (self.name == other.name and
                self.university == other.university and
                self.usn == other.usn)

    def __hash__(self) -> int:
        """Generate hash for student object."""
        return hash((self.name, self.university, self.usn))