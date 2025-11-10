"""
Logging Configuration for Quiz Application
Centralized logging configuration and functions for tracking user actions and system events.
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class QuizLogger:
    """Centralized logger for the quiz application."""

    def __init__(self, log_file: str = "quiz_app.log", log_level: int = logging.INFO):
        """
        Initialize the quiz logger.

        Args:
            log_file: Path to log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self.log_file = log_file
        self.log_level = log_level
        self.logger = None
        self.setup_logger()

    def setup_logger(self) -> None:
        """Configure and set up the logger with rotating file handler."""
        try:
            # Create logger
            self.logger = logging.getLogger('quiz_app')
            self.logger.setLevel(self.log_level)

            # Prevent duplicate handlers
            if self.logger.handlers:
                return

            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            # Create rotating file handler (10MB max, keep 5 backups)
            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)

            # Create console handler for debugging
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.WARNING)  # Only warnings and errors to console
            console_handler.setFormatter(formatter)

            # Add handlers to logger
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

            # Log application start
            self.info("Quiz application logging initialized")

        except Exception as e:
            # Fallback to basic logging if file setup fails
            logging.basicConfig(
                level=self.log_level,
                format='%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            self.logger = logging.getLogger('quiz_app')
            self.error(f"Failed to setup rotating file handler: {e}")

    def info(self, message: str) -> None:
        """
        Log info message.

        Args:
            message: Message to log
        """
        if self.logger:
            self.logger.info(message)

    def error(self, message: str) -> None:
        """
        Log error message.

        Args:
            message: Error message to log
        """
        if self.logger:
            self.logger.error(message)

    def warning(self, message: str) -> None:
        """
        Log warning message.

        Args:
            message: Warning message to log
        """
        if self.logger:
            self.logger.warning(message)

    def debug(self, message: str) -> None:
        """
        Log debug message.

        Args:
            message: Debug message to log
        """
        if self.logger:
            self.logger.debug(message)

    def log_student_registration(self, name: str, university: str, usn: int) -> None:
        """
        Log student registration event.

        Args:
            name: Student name
            university: University name
            usn: Student USN
        """
        self.info(f"Student {name} registered for the quiz (University: {university}, USN: {usn})")

    def log_quiz_start(self, name: str, usn: int) -> None:
        """
        Log quiz start event.

        Args:
            name: Student name
            usn: Student USN
        """
        self.info(f"Quiz started for Student {name} (USN: {usn})")

    def log_question_navigation(self, usn: int, question_number: int) -> None:
        """
        Log question navigation event.

        Args:
            usn: Student USN
            question_number: Current question number
        """
        self.info(f"Student USN {usn} moved to question {question_number}")

    def log_answer_selection(self, usn: int, question_number: int, selected_answer: str) -> None:
        """
        Log answer selection event.

        Args:
            usn: Student USN
            question_number: Question number
            selected_answer: Selected answer option
        """
        self.debug(f"Student USN {usn} selected answer '{selected_answer}' for question {question_number}")

    def log_manual_submission(self, name: str, usn: int, score: int, time_taken: Optional[str] = None) -> None:
        """
        Log manual quiz submission event.

        Args:
            name: Student name
            usn: Student USN
            score: Total score achieved
            time_taken: Time taken for quiz (optional)
        """
        time_info = f" (Time: {time_taken})" if time_taken else ""
        self.info(f"Student {name} (USN: {usn}) ended the exam manually. Total Score: {score}{time_info}")

    def log_automatic_submission(self, name: str, usn: int, score: int) -> None:
        """
        Log automatic quiz submission event (timer expired).

        Args:
            name: Student name
            usn: Student USN
            score: Total score achieved
        """
        self.info(f"Quiz submitted automatically for Student {name} (USN: {usn}). Total Score: {score}")

    def log_database_operation(self, operation: str, success: bool = True, error: Optional[str] = None) -> None:
        """
        Log database operation event.

        Args:
            operation: Description of database operation
            success: Whether operation was successful
            error: Error message if operation failed
        """
        if success:
            self.debug(f"Database operation successful: {operation}")
        else:
            self.error(f"Database operation failed: {operation} - {error}")

    def log_gui_event(self, event: str, details: Optional[str] = None) -> None:
        """
        Log GUI-related events.

        Args:
            event: Description of GUI event
            details: Additional event details (optional)
        """
        message = f"GUI Event: {event}"
        if details:
            message += f" - {details}"
        self.debug(message)

    def log_timer_event(self, event: str, time_remaining: Optional[str] = None) -> None:
        """
        Log timer-related events.

        Args:
            event: Timer event description
            time_remaining: Remaining time (optional)
        """
        message = f"Timer Event: {event}"
        if time_remaining:
            message += f" (Time remaining: {time_remaining})"
        self.debug(message)

    def log_validation_error(self, field: str, value: str, reason: str) -> None:
        """
        Log validation error.

        Args:
            field: Field that failed validation
            value: Invalid value
            reason: Reason for validation failure
        """
        self.warning(f"Validation failed for {field}='{value}': {reason}")

    def log_application_error(self, error: Exception, context: Optional[str] = None) -> None:
        """
        Log application error with context.

        Args:
            error: Exception that occurred
            context: Context where error occurred (optional)
        """
        context_info = f" in {context}" if context else ""
        self.error(f"Application error{context_info}: {type(error).__name__}: {error}")

    def get_log_file_path(self) -> str:
        """
        Get the full path to the log file.

        Returns:
            Full path to log file
        """
        return os.path.abspath(self.log_file)

    def clear_log_file(self) -> None:
        """Clear the current log file."""
        try:
            if os.path.exists(self.log_file):
                # Backup existing log file
                backup_file = f"{self.log_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                os.rename(self.log_file, backup_file)
                self.info(f"Log file backed up to: {backup_file}")

            # Re-initialize logger to create new log file
            for handler in self.logger.handlers[:]:
                handler.close()
                self.logger.removeHandler(handler)

            self.setup_logger()

        except Exception as e:
            self.error(f"Failed to clear log file: {e}")

    def set_log_level(self, level: int) -> None:
        """
        Change the logging level.

        Args:
            level: New logging level
        """
        if self.logger:
            self.logger.setLevel(level)
            for handler in self.logger.handlers:
                handler.setLevel(level)
            self.info(f"Log level changed to: {logging.getLevelName(level)}")


# Global logger instance
_quiz_logger = None


def get_logger() -> QuizLogger:
    """
    Get the global quiz logger instance.

    Returns:
        QuizLogger instance
    """
    global _quiz_logger
    if _quiz_logger is None:
        _quiz_logger = QuizLogger()
    return _quiz_logger


def log_info(message: str) -> None:
    """Convenience function for info logging."""
    get_logger().info(message)


def log_error(message: str) -> None:
    """Convenience function for error logging."""
    get_logger().error(message)


def log_warning(message: str) -> None:
    """Convenience function for warning logging."""
    get_logger().warning(message)


def log_debug(message: str) -> None:
    """Convenience function for debug logging."""
    get_logger().debug(message)