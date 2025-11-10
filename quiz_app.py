#!/usr/bin/env python3
"""
Quiz Application - Main Entry Point
A desktop quiz application built with Python, Tkinter, and SQLite3.

This application allows students to:
1. Register with their name and university
2. Take a 10-question multiple-choice quiz with a 10-minute timer
3. View their results and performance statistics
4. Review their answers after completion

Features:
- Built with Python 3.x and Tkinter
- SQLite3 database for persistent storage
- Comprehensive logging system
- Timer-based automatic submission
- Question navigation and answer review
- Performance statistics and scoring

Usage:
    python quiz_app.py

Requirements:
    - Python 3.7 or higher
    - Tkinter (included with Python)
    - No additional dependencies required

Author: Quiz Application Development Team
Version: 1.0.0
"""

import sys
import os
import traceback
from pathlib import Path

# Add current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import application components
from gui.main_app import QuizApplication
from utils.logger import get_logger


def check_python_version() -> bool:
    """
    Check if Python version meets minimum requirements.

    Returns:
        True if Python version is supported
    """
    required_version = (3, 7)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: Python {sys.version.split()[0]}")
        return False

    return True


def check_tkinter_availability() -> bool:
    """
    Check if Tkinter is available.

    Returns:
        True if Tkinter is available
    """
    try:
        import tkinter
        return True
    except ImportError:
        print("Error: Tkinter is not available on this system.")
        print("Tkinter is typically included with Python installations.")
        print("Please install Tkinter or use a Python distribution that includes it.")
        return False


def setup_application_directory() -> None:
    """Set up application directory and working environment."""
    try:
        # Ensure we're in the correct directory
        app_dir = Path(__file__).parent
        os.chdir(app_dir)

        # Create necessary directories if they don't exist
        directories = ['logs', 'data', 'backups']
        for directory in directories:
            dir_path = app_dir / directory
            dir_path.mkdir(exist_ok=True)
            print(f"Directory ensured: {dir_path}")

    except Exception as e:
        print(f"Error setting up application directory: {e}")


def handle_startup_errors() -> None:
    """Handle startup errors gracefully."""
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions during startup."""
        print("A critical error occurred during application startup:")
        print(f"{exc_type.__name__}: {exc_value}")
        print("\nFull traceback:")
        print(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        print("\nPlease check the log file for more details if available.")
        sys.exit(1)

    sys.excepthook = exception_handler


def display_welcome_message() -> None:
    """Display welcome message and startup information."""
    print("=" * 60)
    print("QUIZ APPLICATION")
    print("=" * 60)
    print("A desktop quiz application with timer and scoring system")
    print("")
    print("Features:")
    print("- Student registration")
    print("- 10-question multiple-choice quiz")
    print("- 10-minute countdown timer")
    print("- Automatic submission on timeout")
    print("- Performance statistics and review")
    print("- Comprehensive logging")
    print("")
    print("Starting application...")
    print("=" * 60)


def display_usage_instructions() -> None:
    """Display usage instructions when help is requested."""
    print("""
Quiz Application - Usage Instructions

USAGE:
    python quiz_app.py [OPTIONS]

OPTIONS:
    -h, --help          Show this help message and exit
    -v, --version       Show version information and exit
    --check-deps        Check system dependencies and exit
    --setup             Initialize application environment only

EXAMPLES:
    python quiz_app.py              # Start the application
    python quiz_app.py --check-deps # Check system requirements
    python quiz_app.py --setup      # Setup environment only

SYSTEM REQUIREMENTS:
    - Python 3.7 or higher
    - Tkinter (GUI framework)
    - 50MB free disk space
    - 512MB RAM minimum

TROUBLESHOOTING:
    If the application fails to start:
    1. Check Python version: python --version
    2. Check Tkinter: python -c "import tkinter"
    3. Verify file permissions
    4. Check available disk space
    5. Review log files for errors

For more information, see README.md
""")


def display_version_info() -> None:
    """Display version information."""
    print("Quiz Application v1.0.0")
    print("Built with Python, Tkinter, and SQLite3")
    print("© 2024 Quiz Application Development Team")


def check_dependencies() -> bool:
    """
    Check system dependencies.

    Returns:
        True if all dependencies are available
    """
    print("Checking system dependencies...")
    print("-" * 40)

    # Check Python version
    print("Python version: ", end="")
    if check_python_version():
        print(f"✓ {sys.version.split()[0]}")
    else:
        print("✗ Unsupported version")
        return False

    # Check Tkinter
    print("Tkinter availability: ", end="")
    if check_tkinter_availability():
        print("✓ Available")
    else:
        print("✗ Not available")
        return False

    # Check available modules
    modules_to_check = ['sqlite3', 'datetime', 'threading', 'logging']
    for module in modules_to_check:
        try:
            __import__(module)
            print(f"Module {module}: ✓ Available")
        except ImportError:
            print(f"Module {module}: ✗ Not available")
            return False

    print("-" * 40)
    print("All dependencies are satisfied!")
    return True


def main() -> None:
    """Main application entry point."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-h', '--help']:
            display_usage_instructions()
            return
        elif arg in ['-v', '--version']:
            display_version_info()
            return
        elif arg == '--check-deps':
            if check_dependencies():
                print("\n✓ System is ready to run the application!")
                sys.exit(0)
            else:
                print("\n✗ Please install missing dependencies before running.")
                sys.exit(1)
        elif arg == '--setup':
            setup_application_directory()
            print("Application environment setup complete!")
            return
        else:
            print(f"Unknown argument: {arg}")
            print("Use --help for usage information.")
            sys.exit(1)

    # Set up error handling
    handle_startup_errors()

    # Display welcome message
    display_welcome_message()

    # Check system requirements
    if not check_python_version():
        sys.exit(1)

    if not check_tkinter_availability():
        sys.exit(1)

    # Setup application directory
    setup_application_directory()

    try:
        # Initialize logging
        logger = get_logger()
        logger.info("Quiz application starting up")

        # Create and run the application
        app = QuizApplication()
        app.run()

    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Failed to start application: {e}"
        print(f"\nError: {error_msg}")
        print("\nFull traceback:")
        print(''.join(traceback.format_exc()))
        print("\nPlease check the following:")
        print("1. Python version is 3.7 or higher")
        print("2. Tkinter is properly installed")
        print("3. Sufficient disk space is available")
        print("4. File permissions are correct")
        print("5. Log file for detailed error information")
        sys.exit(1)


if __name__ == "__main__":
    main()