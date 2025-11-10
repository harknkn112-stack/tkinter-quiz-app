"""
Quiz Configuration File
Central configuration management for the Quiz Application.
Allows customization of quiz parameters without code changes.
"""

import os
import json
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class QuizConfig:
    """Configuration class for quiz settings."""

    # Timer Configuration
    quiz_duration_minutes: int = 10  # Total quiz time in minutes
    timer_warning_times: List[int] = None  # Warning times in seconds (before end)
    show_timer_countdown: bool = True  # Show countdown MM:SS display
    auto_submit_on_timeout: bool = True  # Automatically submit when timer expires

    # Question Configuration
    total_questions: int = 10  # Total number of questions in quiz
    question_distribution: Dict[str, int] = None  # Distribution by difficulty
    enable_question_randomization: bool = True  # Randomize question order
    shuffle_answer_options: bool = False  # Shuffle A/B/C/D order

    # Scoring Configuration
    scoring_marks: Dict[str, int] = None  # Marks per difficulty level
    allow_negative_marking: bool = False  # Enable negative marking
    negative_marking_penalty: int = 1  # Penalty per wrong answer
    show_marks_per_question: bool = False  # Display marks for each question

    # Navigation Configuration
    allow_previous_navigation: bool = True  # Allow going back to previous questions
    allow_question_skip: bool = False  # Allow skipping unanswered questions
    require_all_answers: bool = True  # Require answering all questions

    # Face Detection Configuration
    enable_face_monitoring: bool = True  # Enable face detection monitoring
    camera_index: int = 0  # Camera device index
    face_detection_interval: float = 1.0  # Seconds between face checks
    face_absence_threshold: int = 3  # Consecutive misses before alerting
    face_detection_warnings: int = 3  # Maximum warnings to show

    # UI Configuration
    window_width: int = 800  # Window width in pixels
    window_height: int = 600  # Window height in pixels
    window_resizable: bool = True  # Allow window resizing
    min_window_width: int = 800  # Minimum window width
    min_window_height: int = 600  # Minimum window height
    show_progress_indicator: bool = True  # Show question progress
    show_question_counter: bool = True  # Show "Question X of Y"

    # Student Registration Configuration
    require_name: bool = True  # Require student name
    require_university: bool = True  # Require university name
    name_min_length: int = 2  # Minimum name length
    name_max_length: int = 50  # Maximum name length
    university_min_length: int = 2  # Minimum university length
    university_max_length: int = 100  # Maximum university length

    # Results Configuration
    show_detailed_results: bool = True  # Show detailed breakdown
    show_answer_review: bool = True  # Allow reviewing answers
    show_performance_analysis: bool = True  # Show performance level
    allow_printing_results: bool = True  # Allow printing results
    show_time_taken: bool = True  # Show time taken for quiz

    # Logging Configuration
    enable_logging: bool = True  # Enable application logging
    log_file_name: str = "quiz_app.log"  # Log file name
    log_level: str = "INFO"  # Logging level (DEBUG, INFO, WARNING, ERROR)
    enable_log_rotation: bool = True  # Enable log file rotation
    max_log_size_mb: int = 10  # Maximum log file size in MB
    log_backup_count: int = 5  # Number of log backup files

    # Database Configuration
    database_file: str = "quiz_database.db"  # Database file name
    enable_database_backup: bool = False  # Enable database backups
    backup_interval_hours: int = 24  # Backup interval in hours
    backup_retention_days: int = 7  # Days to keep backups

    # Development/Testing Configuration
    enable_testing_mode: bool = False  # Enable testing features
    mock_questions: bool = False  # Use mock questions for testing
    debug_mode: bool = False  # Enable debug output
    bypass_registration: bool = False  # Skip registration for testing

    def __post_init__(self):
        """Initialize default values for optional fields."""
        if self.timer_warning_times is None:
            self.timer_warning_times = [120, 60, 30, 10]  # 2 min, 1 min, 30 sec, 10 sec

        if self.question_distribution is None:
            self.question_distribution = {
                'simple': 4,      # 4 easy questions
                'medium': 3,      # 3 medium questions
                'complex': 3      # 3 hard questions
            }

        if self.scoring_marks is None:
            self.scoring_marks = {
                'simple': 1,       # 1 mark for easy questions
                'medium': 2,       # 2 marks for medium questions
                'complex': 3       # 3 marks for hard questions
            }


class ConfigurationManager:
    """Manages loading, saving, and accessing quiz configuration."""

    def __init__(self, config_file: str = "quiz_config.json"):
        """
        Initialize configuration manager.

        Args:
            config_file: Path to configuration file
        """
        self.config_file = Path(config_file)
        self.config = QuizConfig()

        # Load configuration if file exists
        if self.config_file.exists():
            self.load_config()
        else:
            # Create default config file
            self.save_config()

    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_file, 'r') as f:
                config_data = json.load(f)

            # Convert dict to QuizConfig object
            self.config = QuizConfig(**config_data)

            # Validate configuration
            self.validate_config()

        except Exception as e:
            print(f"Error loading config: {e}")
            print("Using default configuration.")

    def save_config(self) -> None:
        """Save current configuration to file."""
        try:
            # Convert to dict for JSON serialization
            config_dict = asdict(self.config)

            with open(self.config_file, 'w') as f:
                json.dump(config_dict, f, indent=2, default=str)

            print(f"Configuration saved to {self.config_file}")

        except Exception as e:
            print(f"Error saving config: {e}")

    def validate_config(self) -> None:
        """Validate configuration values."""
        # Validate timer settings
        if self.config.quiz_duration_minutes <= 0:
            raise ValueError("Quiz duration must be positive")

        if self.config.total_questions <= 0:
            raise ValueError("Total questions must be positive")

        # Validate question distribution
        total_dist = sum(self.config.question_distribution.values())
        if total_dist != self.config.total_questions:
            print(f"Warning: Question distribution sum ({total_dist}) doesn't match total questions ({self.config.total_questions})")

        # Validate window sizes
        if self.config.window_width < 400 or self.config.window_height < 300:
            raise ValueError("Window dimensions too small")

        # Validate camera index
        if self.config.camera_index < 0:
            raise ValueError("Camera index must be non-negative")

    def get_config(self) -> QuizConfig:
        """Get current configuration."""
        return self.config

    def update_config(self, **kwargs) -> None:
        """
        Update specific configuration values.

        Args:
            **kwargs: Configuration values to update
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
            else:
                print(f"Warning: Unknown configuration key: {key}")

        # Validate and save updated config
        self.validate_config()
        self.save_config()

    def reset_to_defaults(self) -> None:
        """Reset configuration to default values."""
        self.config = QuizConfig()
        self.save_config()

    def get_timer_settings(self) -> Dict[str, Any]:
        """Get timer-related settings."""
        return {
            'duration_seconds': self.config.quiz_duration_minutes * 60,
            'warning_times': self.config.timer_warning_times,
            'show_countdown': self.config.show_timer_countdown,
            'auto_submit': self.config.auto_submit_on_timeout
        }

    def get_question_settings(self) -> Dict[str, Any]:
        """Get question-related settings."""
        return {
            'total_questions': self.config.total_questions,
            'distribution': self.config.question_distribution,
            'randomize_order': self.config.enable_question_randomization,
            'shuffle_options': self.config.shuffle_answer_options
        }

    def get_scoring_settings(self) -> Dict[str, Any]:
        """Get scoring-related settings."""
        return {
            'marks_per_difficulty': self.config.scoring_marks,
            'negative_marking': self.config.allow_negative_marking,
            'penalty': self.config.negative_marking_penalty,
            'show_marks': self.config.show_marks_per_question
        }

    def get_face_detection_settings(self) -> Dict[str, Any]:
        """Get face detection settings."""
        return {
            'enabled': self.config.enable_face_monitoring,
            'camera_index': self.config.camera_index,
            'detection_interval': self.config.face_detection_interval,
            'absence_threshold': self.config.face_absence_threshold,
            'max_warnings': self.config.face_detection_warnings
        }

    def export_config_summary(self) -> str:
        """Generate a formatted summary of current configuration."""
        summary = []
        summary.append("QUIZ CONFIGURATION SUMMARY")
        summary.append("=" * 50)
        summary.append("")

        summary.append("TIMER SETTINGS:")
        summary.append(f"  Duration: {self.config.quiz_duration_minutes} minutes")
        summary.append(f"  Warning Times: {self.config.timer_warning_times} seconds before end")
        summary.append(f"  Auto Submit: {self.config.auto_submit_on_timeout}")
        summary.append("")

        summary.append("QUESTION SETTINGS:")
        summary.append(f"  Total Questions: {self.config.total_questions}")
        summary.append(f"  Distribution: {self.config.question_distribution}")
        summary.append(f"  Randomize Order: {self.config.enable_question_randomization}")
        summary.append("")

        summary.append("SCORING SETTINGS:")
        summary.append(f"  Marks per Difficulty: {self.config.scoring_marks}")
        summary.append(f"  Negative Marking: {self.config.allow_negative_marking}")
        if self.config.allow_negative_marking:
            summary.append(f"  Penalty: {self.config.negative_marking_penalty} marks")
        summary.append("")

        summary.append("FACE MONITORING:")
        summary.append(f"  Enabled: {self.config.enable_face_monitoring}")
        if self.config.enable_face_monitoring:
            summary.append(f"  Camera Index: {self.config.camera_index}")
            summary.append(f"  Detection Interval: {self.config.face_detection_interval}s")
            summary.append(f"  Absence Threshold: {self.config.face_absence_threshold}")
        summary.append("")

        summary.append("UI SETTINGS:")
        summary.append(f"  Window Size: {self.config.window_width}x{self.config.window_height}")
        summary.append(f"  Progress Indicator: {self.config.show_progress_indicator}")
        summary.append(f"  Question Counter: {self.config.show_question_counter}")
        summary.append("")

        return "\n".join(summary)

    def load_from_env(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'QUIZ_DURATION_MINUTES': ('quiz_duration_minutes', int),
            'TOTAL_QUESTIONS': ('total_questions', int),
            'ENABLE_FACE_MONITORING': ('enable_face_monitoring', bool),
            'CAMERA_INDEX': ('camera_index', int),
            'WINDOW_WIDTH': ('window_width', int),
            'WINDOW_HEIGHT': ('window_height', int),
            'DEBUG_MODE': ('debug_mode', bool),
            'TESTING_MODE': ('enable_testing_mode', bool)
        }

        for env_var, (config_attr, converter) in env_mappings.items():
            if env_var in os.environ:
                try:
                    value = converter(os.environ[env_var])
                    setattr(self.config, config_attr, value)
                except (ValueError, AttributeError):
                    print(f"Warning: Invalid value for {env_var}: {os.environ[env_var]}")


# Global configuration instance
_config_manager = ConfigurationManager()


def get_config() -> QuizConfig:
    """Get the current configuration."""
    return _config_manager.get_config()


def update_config(**kwargs) -> None:
    """Update configuration values."""
    _config_manager.update_config(**kwargs)


def save_config() -> None:
    """Save current configuration."""
    _config_manager.save_config()


def export_config_summary() -> str:
    """Export configuration summary."""
    return _config_manager.export_config_summary()


def reset_config() -> None:
    """Reset configuration to defaults."""
    _config_manager.reset_to_defaults()


def load_from_env() -> None:
    """Load configuration from environment variables."""
    _config_manager.load_from_env()


# Convenience functions for common configuration tasks
def get_quiz_duration() -> int:
    """Get quiz duration in seconds."""
    return get_config().quiz_duration_minutes * 60


def get_total_questions() -> int:
    """Get total number of questions."""
    return get_config().total_questions


def is_face_monitoring_enabled() -> bool:
    """Check if face monitoring is enabled."""
    return get_config().enable_face_monitoring


def get_window_size() -> tuple:
    """Get window size as (width, height)."""
    config = get_config()
    return (config.window_width, config.window_height)


# Main execution for configuration management
if __name__ == "__main__":
    print("Quiz Configuration Management")
    print("=" * 40)

    print("\nCurrent Configuration:")
    print(export_config_summary())

    print("\nConfiguration Options:")
    print("1. View current config: python -c 'from quiz_config import get_config; print(get_config().__dict__)'")
    print("2. Update setting: python -c 'from quiz_config import update_config; update_config(quiz_duration_minutes=15)'")
    print("3. Reset to defaults: python -c 'from quiz_config import reset_config; reset_config()'")
    print("4. Load from environment: python -c 'from quiz_config import load_from_env; load_from_env()'")