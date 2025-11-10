"""
Database Manager for Quiz Application
Handles all database operations including initialization, student registration,
score storage, and question retrieval.
"""

import sqlite3
import os
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database operations for the quiz application."""

    def __init__(self, db_path: str = "quiz_database.db"):
        """
        Initialize database manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.connection = None
        self.initialize_database()

    def initialize_database(self) -> None:
        """Create database tables if they don't exist."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON")

            # Create Questions table
            create_questions_table = """
            CREATE TABLE IF NOT EXISTS Questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                option4 TEXT NOT NULL,
                correct TEXT NOT NULL,
                marks INTEGER NOT NULL,
                type TEXT NOT NULL CHECK (type IN ('simple', 'medium', 'complex'))
            );
            """

            # Create Student table
            create_student_table = """
            CREATE TABLE IF NOT EXISTS Student (
                usn INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                university TEXT NOT NULL,
                date_of_exam TEXT NOT NULL,
                marks_scored INTEGER DEFAULT 0
            );
            """

            self.connection.execute(create_questions_table)
            self.connection.execute(create_student_table)
            self.connection.commit()

        except sqlite3.Error as e:
            raise Exception(f"Database initialization failed: {e}")

    def save_student(self, name: str, university: str) -> int:
        """
        Save student information to database.

        Args:
            name: Student name
            university: University name

        Returns:
            Generated USN (Unique Student Number)

        Raises:
            Exception: If database operation fails
        """
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %I:%M%p")

            cursor = self.connection.cursor()
            cursor.execute(
                """
                INSERT INTO Student (name, university, date_of_exam)
                VALUES (?, ?, ?)
                """,
                (name, university, current_time)
            )

            usn = cursor.lastrowid
            self.connection.commit()

            return usn

        except sqlite3.Error as e:
            self.connection.rollback()
            raise Exception(f"Failed to save student data: {e}")

    def get_questions(self) -> List[Dict]:
        """
        Retrieve 10 questions from database (4 simple, 3 medium, 3 complex).

        Returns:
            List of question dictionaries

        Raises:
            Exception: If database operation fails
        """
        try:
            cursor = self.connection.cursor()

            # Get 4 simple questions
            simple_questions = cursor.execute(
                "SELECT * FROM Questions WHERE type = 'simple' ORDER BY RANDOM() LIMIT 4"
            ).fetchall()

            # Get 3 medium questions
            medium_questions = cursor.execute(
                "SELECT * FROM Questions WHERE type = 'medium' ORDER BY RANDOM() LIMIT 3"
            ).fetchall()

            # Get 3 complex questions
            complex_questions = cursor.execute(
                "SELECT * FROM Questions WHERE type = 'complex' ORDER BY RANDOM() LIMIT 3"
            ).fetchall()

            # Combine and convert to list of dictionaries
            all_questions = simple_questions + medium_questions + complex_questions
            questions_list = []

            for row in all_questions:
                question_dict = {
                    'id': row[0],
                    'question': row[1],
                    'option1': row[2],
                    'option2': row[3],
                    'option3': row[4],
                    'option4': row[5],
                    'correct': row[6],
                    'marks': row[7],
                    'type': row[8]
                }
                questions_list.append(question_dict)

            return questions_list

        except sqlite3.Error as e:
            raise Exception(f"Failed to retrieve questions: {e}")

    def save_score(self, usn: int, score: int) -> bool:
        """
        Update student record with final score.

        Args:
            usn: Student USN
            score: Total marks scored

        Returns:
            True if successful, False otherwise

        Raises:
            Exception: If database operation fails
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "UPDATE Student SET marks_scored = ? WHERE usn = ?",
                (score, usn)
            )

            self.connection.commit()
            return cursor.rowcount > 0

        except sqlite3.Error as e:
            self.connection.rollback()
            raise Exception(f"Failed to save score: {e}")

    def get_student_info(self, usn: int) -> Optional[Dict]:
        """
        Retrieve student information by USN.

        Args:
            usn: Student USN

        Returns:
            Student dictionary or None if not found
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT usn, name, university, date_of_exam, marks_scored FROM Student WHERE usn = ?",
                (usn,)
            )

            row = cursor.fetchone()
            if row:
                return {
                    'usn': row[0],
                    'name': row[1],
                    'university': row[2],
                    'date_of_exam': row[3],
                    'marks_scored': row[4]
                }
            return None

        except sqlite3.Error as e:
            raise Exception(f"Failed to get student info: {e}")

    def get_question_count_by_type(self, question_type: str) -> int:
        """
        Get count of questions by type.

        Args:
            question_type: Type of question ('simple', 'medium', 'complex')

        Returns:
            Number of questions of specified type
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM Questions WHERE type = ?",
                (question_type,)
            )

            return cursor.fetchone()[0]

        except sqlite3.Error as e:
            raise Exception(f"Failed to get question count: {e}")

    def is_database_empty(self) -> bool:
        """
        Check if questions table is empty.

        Returns:
            True if no questions in database
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM Questions")
            return cursor.fetchone()[0] == 0

        except sqlite3.Error as e:
            raise Exception(f"Failed to check database status: {e}")

    def close_connection(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connection()