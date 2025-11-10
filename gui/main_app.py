"""
Main Application Controller for Quiz Application
Orchestrates the entire quiz application flow and manages screen transitions.
"""

import tkinter as tk
from tkinter import messagebox
import sys
import traceback
from typing import Optional

from database.db_manager import DatabaseManager
from models.student import Student
from models.question import Question, QuestionBank
from utils.logger import get_logger
from utils.sample_data import populate_database
from gui.registration import RegistrationScreen
from gui.quiz_screen import QuizScreen
from gui.results import ResultsScreen
from gui.analytics_screen import AnalyticsScreen
from quiz_config import get_config


class QuizApplication:
    """Main application controller for the quiz system."""

    def __init__(self):
        """Initialize the quiz application."""
        self.root = tk.Tk()
        self.logger = get_logger()
        self.db_manager = None
        self.student = None
        self.questions = []
        self.answers = []

        # Screen objects
        self.registration_screen = None
        self.quiz_screen = None
        self.results_screen = None
        self.analytics_screen = None

        # Application state
        self.is_initialized = False
        self.is_quiz_active = False

        # Initialize application
        self.setup_application()
        self.setup_database()
        self.create_screens()

    def setup_application(self) -> None:
        """Set up the main application window."""
        try:
            # Configure main window
            self.root.title("Quiz Application")
            self.root.geometry("800x600")
            self.root.minsize(800, 600)
            self.root.configure(bg="#ecf0f1")

            # Center window on screen
            self.center_window()

            # Handle window close event
            self.root.protocol("WM_DELETE_WINDOW", self.on_application_close)

            # Set up error handling
            self.setup_error_handling()

            self.logger.info("Quiz application window initialized")

        except Exception as e:
            self.handle_critical_error("Application Setup Error", e)

    def center_window(self) -> None:
        """Center the application window on the screen."""
        try:
            self.root.update_idletasks()
            width = self.root.winfo_width()
            height = self.root.winfo_height()
            x = (self.root.winfo_screenwidth() // 2) - (width // 2)
            y = (self.root.winfo_screenheight() // 2) - (height // 2)
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        except Exception as e:
            self.logger.warning(f"Failed to center window: {e}")

    def setup_error_handling(self) -> None:
        """Set up global error handling."""
        def handle_tk_error(exc_type, exc_value, exc_traceback):
            """Handle uncaught exceptions."""
            error_msg = f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}"
            self.logger.log_application_error(exc_value, "uncaught_exception")
            messagebox.showerror("Application Error", error_msg)
            self.on_application_close()

        # Set up exception handler (if available)
        sys.excepthook = handle_tk_error

    def setup_database(self) -> None:
        """Initialize the database connection."""
        try:
            self.db_manager = DatabaseManager()

            # Check if database is empty and populate with sample data
            if self.db_manager.is_database_empty():
                self.logger.info("Database is empty, populating with sample questions")
                populate_database(self.db_manager)
                self.logger.info("Sample questions populated successfully")

            self.logger.info("Database initialized successfully")

        except Exception as e:
            error_msg = f"Failed to initialize database: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Database Error", error_msg)
            self.on_application_close()

    def create_screens(self) -> None:
        """Create all application screens."""
        try:
            # Create registration screen
            self.registration_screen = RegistrationScreen(
                master=self.root,
                on_registration_success=self.on_registration_success,
                on_cancel=self.on_registration_cancel,
                on_analytics=self.show_analytics_screen
            )

            # Hide other screens initially
            if self.registration_screen:
                self.registration_screen.show_frame()

            self.is_initialized = True
            self.logger.info("Application screens created successfully")

        except Exception as e:
            self.handle_critical_error("Screen Creation Error", e)

    def on_registration_success(self, student: Student) -> None:
        """
        Handle successful student registration.

        Args:
            student: Registered student object
        """
        try:
            # Save student to database
            usn = self.db_manager.save_student(student.name, student.university)
            student.usn = usn

            self.student = student
            self.logger.log_student_registration(student.name, student.university, usn)

            # Load questions for quiz
            self.load_quiz_questions()

            # Transition to quiz screen
            self.show_quiz_screen()

        except Exception as e:
            error_msg = f"Failed to process registration: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Registration Error", error_msg)

    def on_registration_cancel(self) -> None:
        """Handle registration cancellation."""
        try:
            result = messagebox.askyesno(
                "Exit Application",
                "Are you sure you want to exit the quiz application?",
                icon="question"
            )

            if result:
                self.on_application_close()

        except Exception as e:
            self.logger.log_application_error(e, "registration_cancel")

    def load_quiz_questions(self) -> None:
        """Load questions from database for the quiz."""
        try:
            # Get questions from database
            questions_data = self.db_manager.get_questions()

            if len(questions_data) < 10:
                raise Exception(f"Insufficient questions in database: {len(questions_data)}/10")

            # Convert to Question objects
            self.questions = []
            for q_data in questions_data:
                question = Question(
                    question_text=q_data['question'],
                    options=[q_data['option1'], q_data['option2'], q_data['option3'], q_data['option4']],
                    correct_answer=q_data['correct'],
                    marks=q_data['marks'],
                    difficulty=q_data['type'],
                    question_id=q_data['id']
                )
                self.questions.append(question)

            self.logger.info(f"Loaded {len(self.questions)} questions for quiz")

        except Exception as e:
            error_msg = f"Failed to load quiz questions: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Question Loading Error", error_msg)
            raise

    def show_quiz_screen(self) -> None:
        """Show the quiz screen."""
        try:
            # Hide registration screen
            if self.registration_screen:
                self.registration_screen.hide_frame()

            # Create quiz screen
            self.quiz_screen = QuizScreen(
                master=self.root,
                questions=self.questions,
                student=self.student,
                on_quiz_complete=self.on_quiz_complete,
                on_quiz_cancel=self.on_quiz_cancel
            )

            if self.quiz_screen:
                self.quiz_screen.show_frame()
                self.is_quiz_active = True
                self.logger.info("Quiz screen displayed")

        except Exception as e:
            self.handle_critical_error("Quiz Screen Error", e)

    def on_quiz_complete(self, student: Student, answers: list) -> None:
        """
        Handle quiz completion.

        Args:
            student: Student who completed the quiz
            answers: List of student's answers
        """
        try:
            self.is_quiz_active = False
            self.answers = answers

            # Save score to database
            self.db_manager.save_score(student.usn, student.marks_scored)

            self.logger.info(f"Quiz completed for {student.name} with score {student.marks_scored}")

            # Show results screen
            self.show_results_screen()

        except Exception as e:
            error_msg = f"Failed to process quiz completion: {e}"
            self.logger.error(error_msg)
            messagebox.showerror("Quiz Completion Error", error_msg)

    def on_quiz_cancel(self) -> None:
        """Handle quiz cancellation."""
        try:
            result = messagebox.askyesno(
                "Cancel Quiz",
                "Are you sure you want to cancel the quiz? Your progress will be lost.",
                icon="warning"
            )

            if result:
                self.is_quiz_active = False
                if self.quiz_screen:
                    self.quiz_screen.cleanup()
                    self.quiz_screen.hide_frame()

                # Return to registration screen
                if self.registration_screen:
                    self.registration_screen.show_frame()

                self.logger.info("Quiz cancelled by user")

        except Exception as e:
            self.logger.log_application_error(e, "quiz_cancel")

    def show_results_screen(self) -> None:
        """Show the results screen."""
        try:
            # Hide quiz screen
            if self.quiz_screen:
                self.quiz_screen.hide_frame()
                self.quiz_screen.cleanup()

            # Create results screen
            self.results_screen = ResultsScreen(
                master=self.root,
                student=self.student,
                questions=self.questions,
                answers=self.answers,
                on_exit=self.on_results_exit,
                on_review=self.on_results_review
            )

            if self.results_screen:
                self.results_screen.show_frame()
                self.logger.info("Results screen displayed")

        except Exception as e:
            self.handle_critical_error("Results Screen Error", e)

    def on_results_exit(self) -> None:
        """Handle exit from results screen."""
        self.on_application_close()

    def on_results_review(self) -> None:
        """Handle answer review request."""
        try:
            # This would implement an answer review screen
            # For now, just show a simple summary
            review_data = self.results_screen.get_detailed_answer_review()
            self.show_answer_review(review_data)

        except Exception as e:
            self.logger.log_application_error(e, "answer_review")

    def show_analytics_screen(self) -> None:
        """Show the analytics screen."""
        try:
            # Hide current screen
            if self.registration_screen:
                self.registration_screen.hide_frame()
            if self.results_screen:
                self.results_screen.hide_frame()

            # Create analytics screen if it doesn't exist
            if not self.analytics_screen:
                self.analytics_screen = AnalyticsScreen(
                    master=self.root,
                    on_back=self.hide_analytics_screen
                )

            if self.analytics_screen:
                self.analytics_screen.show_frame()
                self.logger.info("Analytics screen displayed")

        except Exception as e:
            self.handle_critical_error("Analytics Screen Error", e)

    def hide_analytics_screen(self) -> None:
        """Hide the analytics screen and return to registration."""
        try:
            if self.analytics_screen:
                self.analytics_screen.hide_frame()

            # Show registration screen
            if self.registration_screen:
                self.registration_screen.show_frame()

            self.logger.info("Returned to registration screen from analytics")

        except Exception as e:
            self.logger.log_application_error(e, "hide_analytics")

    def show_answer_review(self, review_data: list) -> None:
        """
        Show a simple answer review dialog.

        Args:
            review_data: List of question and answer details
        """
        try:
            review_window = tk.Toplevel(self.root)
            review_window.title("Answer Review")
            review_window.geometry("700x500")
            review_window.configure(bg="white")

            # Create scrollable frame
            canvas = tk.Canvas(review_window, bg="white")
            scrollbar = ttk.Scrollbar(review_window, orient="vertical", command=canvas.yview)
            scrollable_frame = ttk.Frame(canvas)

            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )

            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)

            # Add content
            for i, item in enumerate(review_data):
                frame = ttk.LabelFrame(scrollable_frame, text=f"Question {item['question_number']}", padding="10")
                frame.pack(fill=tk.X, padx=10, pady=5)

                # Question
                question_label = ttk.Label(frame, text=item['question_text'], wraplength=600)
                question_label.pack(anchor=tk.W)

                # Options with indicators
                for j, option in enumerate(item['options']):
                    option_text = f"{'ABCDEFGH'[j]}. {option}"

                    if option == item['correct_answer']:
                        option_text += " ✓ (Correct)"
                        color = "green"
                    elif option == item['student_answer'] and option != item['correct_answer']:
                        option_text += " ✗ (Your Answer)"
                        color = "red"
                    else:
                        option_text += " (Your Answer)" if option == item['student_answer'] else ""
                        color = "black"

                    option_label = ttk.Label(frame, text=option_text, foreground=color)
                    option_label.pack(anchor=tk.W, padx=(20, 0))

                # Status
                if item['answered']:
                    status_text = f"Answered: {'Correct' if item['is_correct'] else 'Incorrect'} ({item['marks']} marks)"
                    status_color = "green" if item['is_correct'] else "red"
                else:
                    status_text = f"Not answered (0/{item['marks']} marks)"
                    status_color = "orange"

                status_label = ttk.Label(frame, text=status_text, foreground=status_color)
                status_label.pack(anchor=tk.W, pady=(5, 0))

            # Close button
            close_button = ttk.Button(review_window, text="Close", command=review_window.destroy)
            close_button.pack(pady=10)

            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")

        except Exception as e:
            messagebox.showerror("Review Error", f"Failed to show answer review: {e}")

    def handle_critical_error(self, error_title: str, error: Exception) -> None:
        """
        Handle critical application errors.

        Args:
            error_title: Title for error dialog
            error: Exception that occurred
        """
        error_msg = f"{error_title}:\n{str(error)}"
        self.logger.error(error_msg)
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        messagebox.showerror(error_title, error_msg)
        self.on_application_close()

    def on_application_close(self) -> None:
        """Handle application close event."""
        try:
            self.logger.info("Application closing")

            # Cleanup resources
            if self.quiz_screen:
                self.quiz_screen.cleanup()

            if self.analytics_screen:
                self.analytics_screen.analytics.close_connection()

            if self.db_manager:
                self.db_manager.close_connection()

            # Close application
            self.root.quit()
            self.root.destroy()

        except Exception as e:
            print(f"Error during application shutdown: {e}")
            sys.exit(1)

    def run(self) -> None:
        """Start the application main loop."""
        try:
            if self.is_initialized:
                self.logger.info("Starting application main loop")
                self.root.mainloop()
            else:
                self.logger.error("Application failed to initialize properly")
                sys.exit(1)

        except KeyboardInterrupt:
            self.logger.info("Application interrupted by user")
            self.on_application_close()
        except Exception as e:
            self.handle_critical_error("Runtime Error", e)


def main():
    """Main entry point for the application."""
    try:
        app = QuizApplication()
        app.run()
    except Exception as e:
        print(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()