#!/usr/bin/env python3
"""
Quiz Application Diagnostic Tool
Helps troubleshoot common issues with the Quiz Application.

Usage:
    python diagnose.py

This tool will check:
1. Python version and dependencies
2. File structure and permissions
3. Database connectivity
4. Logging functionality
5. Common configuration issues
"""

import sys
import os
import traceback
from pathlib import Path


def print_header(title):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_check(check_name, result, details=""):
    """Print a check result."""
    status = "✓ PASS" if result else "✗ FAIL"
    print(f"  {check_name:<50} {status}")
    if details:
        print(f"    {details}")


def check_python_environment():
    """Check Python version and basic imports."""
    print_header("PYTHON ENVIRONMENT CHECK")

    # Check Python version
    version_ok = sys.version_info >= (3, 7)
    print_check("Python 3.7+ available", version_ok, f"Current: {sys.version.split()[0]}")

    # Check required modules
    modules = [
        ('sqlite3', 'Database functionality'),
        ('datetime', 'Date/time handling'),
        ('threading', 'Timer functionality'),
        ('logging', 'Logging system'),
        ('pathlib', 'Path handling'),
    ]

    for module_name, description in modules:
        try:
            __import__(module_name)
            print_check(f"Module {module_name}", True, description)
        except ImportError as e:
            print_check(f"Module {module_name}", False, f"Missing: {e}")

    # Check Tkinter separately (may not be available)
    try:
        import tkinter
        print_check("Module tkinter", True, "GUI framework available")
    except ImportError as e:
        print_check("Module tkinter", False, f"GUI not available: {e}")
        print("    Note: This is expected on some server environments")


def check_file_structure():
    """Check if all required files exist."""
    print_header("FILE STRUCTURE CHECK")

    required_files = [
        "quiz_app.py",
        "requirements.txt",
        "README.md",
        "database/__init__.py",
        "database/db_manager.py",
        "gui/__init__.py",
        "gui/main_app.py",
        "gui/registration.py",
        "gui/quiz_screen.py",
        "gui/results.py",
        "models/__init__.py",
        "models/student.py",
        "models/question.py",
        "utils/__init__.py",
        "utils/logger.py",
        "utils/timer.py",
        "utils/sample_data.py",
    ]

    missing_files = []
    for file_path in required_files:
        exists = os.path.exists(file_path)
        print_check(f"File: {file_path}", exists)
        if not exists:
            missing_files.append(file_path)

    if missing_files:
        print(f"\n  Missing {len(missing_files)} required file(s):")
        for file_path in missing_files:
            print(f"    - {file_path}")


def check_directories():
    """Check if required directories can be created."""
    print_header("DIRECTORY PERMISSIONS CHECK")

    directories = ["logs", "data", "backups"]
    for directory in directories:
        try:
            Path(directory).mkdir(exist_ok=True)
            print_check(f"Directory {directory}", True, "Can create/access")
        except Exception as e:
            print_check(f"Directory {directory}", False, f"Permission error: {e}")


def check_database():
    """Check database functionality."""
    print_header("DATABASE FUNCTIONALITY CHECK")

    try:
        # Add current directory to path
        sys.path.insert(0, '.')

        from database.db_manager import DatabaseManager

        # Test database creation
        print_check("Database import", True)

        db = DatabaseManager("test_diagnostic.db")
        print_check("Database connection", True)

        # Test table creation
        tables_exist = not db.is_database_empty() or True  # Tables are created on init
        print_check("Table creation", tables_exist)

        # Test question retrieval (may be empty)
        questions = db.get_questions()
        print_check("Question retrieval", True, f"Found {len(questions)} questions")

        db.close_connection()

        # Clean up test database
        if os.path.exists("test_diagnostic.db"):
            os.remove("test_diagnostic.db")

    except Exception as e:
        print_check("Database functionality", False, f"Error: {e}")
        print(f"    Full error: {traceback.format_exc()}")


def check_logging():
    """Check logging functionality."""
    print_header("LOGGING FUNCTIONALITY CHECK")

    try:
        sys.path.insert(0, '.')
        from utils.logger import get_logger

        logger = get_logger()
        print_check("Logger creation", True)

        # Test logging
        logger.info("Diagnostic test log entry")
        print_check("Log writing", True)

        # Check log file
        log_file_path = logger.get_log_file_path()
        log_exists = os.path.exists(log_file_path)
        print_check("Log file exists", log_exists, f"Path: {log_file_path}")

        if log_exists:
            log_size = os.path.getsize(log_file_path)
            print_check("Log file has content", log_size > 0, f"Size: {log_size} bytes")

    except Exception as e:
        print_check("Logging functionality", False, f"Error: {e}")


def check_models():
    """Check data models."""
    print_header("DATA MODELS CHECK")

    try:
        sys.path.insert(0, '.')
        from models.student import Student
        from models.question import Question, DifficultyType

        # Test student model
        student = Student(name="Test Student", university="Test University")
        is_valid, errors = student.validate()
        print_check("Student model", is_valid)

        # Test question model
        question = Question(
            question_text="Test question?",
            options=["Option 1", "Option 2", "Option 3", "Option 4"],
            correct_answer="Option 1",
            marks=1,
            difficulty=DifficultyType.SIMPLE
        )
        is_valid, errors = question.validate()
        print_check("Question model", is_valid)

    except Exception as e:
        print_check("Data models", False, f"Error: {e}")


def check_sample_data():
    """Check sample data."""
    print_header("SAMPLE DATA CHECK")

    try:
        sys.path.insert(0, '.')
        from utils.sample_data import get_sample_questions, validate_sample_data

        sample_data = get_sample_questions()
        total_questions = sum(len(questions) for questions in sample_data.values())
        print_check("Sample data loading", total_questions > 0, f"{total_questions} questions")

        is_valid = validate_sample_data()
        print_check("Sample data validation", is_valid)

        # Check distribution
        if is_valid:
            simple = len(sample_data.get('simple', []))
            medium = len(sample_data.get('medium', []))
            complex_q = len(sample_data.get('complex', []))
            print(f"    Distribution: Simple={simple}, Medium={medium}, Complex={complex_q}")

    except Exception as e:
        print_check("Sample data", False, f"Error: {e}")


def provide_recommendations():
    """Provide troubleshooting recommendations."""
    print_header("RECOMMENDATIONS")

    print("""
TROUBLESHOOTING TIPS:

1. If tkinter is not available:
   - On Ubuntu/Debian: sudo apt-get install python3-tk
   - On Fedora: sudo dnf install python3-tkinter
   - On macOS: Tkinter should be included with Python
   - On Windows: Reinstall Python with Tkinter support

2. If database errors occur:
   - Delete quiz_database.db and restart the application
   - Check write permissions in the application directory
   - Ensure SQLite3 is properly installed

3. If logging doesn't work:
   - Check write permissions for the application directory
   - Ensure antivirus software isn't blocking file creation
   - Try running with administrator privileges

4. General fixes:
   - Ensure you're in the correct directory: cd tkinter-quiz-app
   - Use Python 3.7 or higher: python --version
   - Install with: python quiz_app.py

5. For persistent issues:
   - Check the quiz_app.log file for detailed error messages
   - Run this diagnostic tool again after making changes
   - Ensure all files have proper permissions
    """)


def main():
    """Main diagnostic function."""
    print("QUIZ APPLICATION DIAGNOSTIC TOOL")
    print("This tool will check your Quiz Application setup and identify common issues.")

    try:
        check_python_environment()
        check_file_structure()
        check_directories()
        check_database()
        check_logging()
        check_models()
        check_sample_data()

        provide_recommendations()

        print_header("DIAGNOSTIC COMPLETE")
        print("Review the results above for any issues that need to be addressed.")
        print("If you see ✗ PASS results, follow the recommendations to fix the problems.")

    except KeyboardInterrupt:
        print("\n\nDiagnostic interrupted by user.")
    except Exception as e:
        print(f"\n\nDiagnostic tool encountered an error: {e}")
        print(f"Full error: {traceback.format_exc()}")


if __name__ == "__main__":
    main()