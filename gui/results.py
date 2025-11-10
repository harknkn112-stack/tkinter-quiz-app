"""
Results Screen for Quiz Application
Displays final score and quiz statistics to students.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from models.student import Student
from models.question import Question
from utils.logger import get_logger


class ResultsScreen:
    """Results screen for displaying quiz outcomes."""

    def __init__(self, master: tk.Tk,
                 student: Student,
                 questions: List[Question],
                 answers: List[str],
                 on_exit: Optional[Callable[[], None]] = None,
                 on_review: Optional[Callable[[], None]] = None):
        """
        Initialize results screen.

        Args:
            master: Parent tkinter window
            student: Student object who took the quiz
            questions: List of questions from the quiz
            answers: List of student's answers
            on_exit: Callback when user exits application
            on_review: Callback when user wants to review answers
        """
        self.master = master
        self.student = student
        self.questions = questions
        self.answers = answers
        self.on_exit = on_exit
        self.on_review = on_review
        self.logger = get_logger()

        # Calculate results
        self.calculate_results()

        # Create results frame
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Configure styles
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Bind keyboard events
        self.bind_keyboard_events()

    def setup_styles(self) -> None:
        """Configure ttk styles for the results screen."""
        style = ttk.Style()

        # Title style
        style.configure("Title.TLabel",
                       font=("Arial", 20, "bold"),
                       foreground="#2c3e50")

        # Subtitle style
        style.configure("Subtitle.TLabel",
                       font=("Arial", 12),
                       foreground="#7f8c8d")

        # Score style
        style.configure("Score.TLabel",
                       font=("Arial", 18, "bold"),
                       foreground="#27ae60")

        # Percentage style
        style.configure("Percentage.TLabel",
                       font=("Arial", 16, "bold"),
                       foreground="#3498db")

        # Field label style
        style.configure("Field.TLabel",
                       font=("Arial", 11, "bold"),
                       foreground="#2c3e50")

        # Value style
        style.configure("Value.TLabel",
                       font=("Arial", 11),
                       foreground="#2c3e50")

        # Button styles
        style.configure("Action.TButton",
                       font=("Arial", 11, "bold"),
                       padding=(20, 10))

        style.configure("Secondary.TButton",
                       font=("Arial", 10),
                       padding=(15, 8))

    def calculate_results(self) -> None:
        """Calculate quiz results statistics."""
        self.correct_count = 0
        self.incorrect_count = 0
        self.unanswered_count = 0
        self.total_possible_marks = 0
        self.total_achieved_marks = 0

        for i, question in enumerate(self.questions):
            self.total_possible_marks += question.marks

            if i < len(self.answers) and self.answers[i]:
                # Convert radio value to actual answer text
                if self.answers[i].startswith("option"):
                    option_num = int(self.answers[i].replace("option", "")) - 1
                    selected_answer = question.get_option(option_num)

                    if question.check_answer(selected_answer):
                        self.correct_count += 1
                        self.total_achieved_marks += question.marks
                    else:
                        self.incorrect_count += 1
            else:
                self.unanswered_count += 1

        # Calculate percentage
        if self.total_possible_marks > 0:
            self.percentage = (self.total_achieved_marks / self.total_possible_marks) * 100
        else:
            self.percentage = 0

        # Determine performance level
        if self.percentage >= 80:
            self.performance_level = "Excellent"
            self.performance_color = "#27ae60"
        elif self.percentage >= 60:
            self.performance_level = "Good"
            self.performance_color = "#3498db"
        elif self.percentage >= 40:
            self.performance_level = "Satisfactory"
            self.performance_color = "#f39c12"
        else:
            self.performance_level = "Needs Improvement"
            self.performance_color = "#e74c3c"

    def create_widgets(self) -> None:
        """Create all widgets for the results screen."""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title section
        self.create_title_section(main_frame)

        # Score section
        self.create_score_section(main_frame)

        # Student info section
        self.create_student_info_section(main_frame)

        # Statistics section
        self.create_statistics_section(main_frame)

        # Action buttons section
        self.create_button_section(main_frame)

    def create_title_section(self, parent: ttk.Frame) -> None:
        """Create title and subtitle."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        # Main title
        title_label = ttk.Label(
            title_frame,
            text="Quiz Results",
            style="Title.TLabel"
        )
        title_label.pack()

        # Performance level
        performance_label = ttk.Label(
            title_frame,
            text=self.performance_level,
            font=("Arial", 14, "bold"),
            foreground=self.performance_color
        )
        performance_label.pack(pady=(10, 0))

    def create_score_section(self, parent: ttk.Frame) -> None:
        """Create the main score display."""
        score_frame = ttk.LabelFrame(parent, text="Final Score", padding="20")
        score_frame.pack(fill=tk.X, pady=20)

        # Score display
        score_label = ttk.Label(
            score_frame,
            text=f"{self.total_achieved_marks} / {self.total_possible_marks}",
            style="Score.TLabel"
        )
        score_label.pack()

        # Percentage display
        percentage_label = ttk.Label(
            score_frame,
            text=f"{self.percentage:.1f}%",
            style="Percentage.TLabel"
        )
        percentage_label.pack(pady=(10, 0))

    def create_student_info_section(self, parent: ttk.Frame) -> None:
        """Create student information section."""
        info_frame = ttk.LabelFrame(parent, text="Student Information", padding="15")
        info_frame.pack(fill=tk.X, pady=20)

        # Student name
        name_row = ttk.Frame(info_frame)
        name_row.pack(fill=tk.X, pady=5)

        name_label = ttk.Label(name_row, text="Name:", style="Field.TLabel", width=15)
        name_label.pack(side=tk.LEFT)

        name_value = ttk.Label(name_row, text=self.student.display_name, style="Value.TLabel")
        name_value.pack(side=tk.LEFT)

        # University
        university_row = ttk.Frame(info_frame)
        university_row.pack(fill=tk.X, pady=5)

        university_label = ttk.Label(university_row, text="University:", style="Field.TLabel", width=15)
        university_label.pack(side=tk.LEFT)

        university_value = ttk.Label(university_row, text=self.student.display_university, style="Value.TLabel")
        university_value.pack(side=tk.LEFT)

        # Time taken
        time_row = ttk.Frame(info_frame)
        time_row.pack(fill=tk.X, pady=5)

        time_label = ttk.Label(time_row, text="Time Taken:", style="Field.TLabel", width=15)
        time_label.pack(side=tk.LEFT)

        time_value = ttk.Label(time_row, text=self.student.get_formatted_time_taken(), style="Value.TLabel")
        time_value.pack(side=tk.LEFT)

        # Exam date
        date_row = ttk.Frame(info_frame)
        date_row.pack(fill=tk.X, pady=5)

        date_label = ttk.Label(date_row, text="Exam Date:", style="Field.TLabel", width=15)
        date_label.pack(side=tk.LEFT)

        date_value = ttk.Label(date_row, text=self.student.date_of_exam, style="Value.TLabel")
        date_value.pack(side=tk.LEFT)

    def create_statistics_section(self, parent: ttk.Frame) -> None:
        """Create quiz statistics section."""
        stats_frame = ttk.LabelFrame(parent, text="Quiz Statistics", padding="15")
        stats_frame.pack(fill=tk.X, pady=20)

        # Correct answers
        correct_row = ttk.Frame(stats_frame)
        correct_row.pack(fill=tk.X, pady=5)

        correct_label = ttk.Label(correct_row, text="Correct Answers:", style="Field.TLabel", width=15)
        correct_label.pack(side=tk.LEFT)

        correct_value = ttk.Label(correct_row, text=f"{self.correct_count}",
                                 style="Value.TLabel", foreground="#27ae60")
        correct_value.pack(side=tk.LEFT)

        # Incorrect answers
        incorrect_row = ttk.Frame(stats_frame)
        incorrect_row.pack(fill=tk.X, pady=5)

        incorrect_label = ttk.Label(incorrect_row, text="Incorrect Answers:", style="Field.TLabel", width=15)
        incorrect_label.pack(side=tk.LEFT)

        incorrect_value = ttk.Label(incorrect_row, text=f"{self.incorrect_count}",
                                   style="Value.TLabel", foreground="#e74c3c")
        incorrect_value.pack(side=tk.LEFT)

        # Unanswered questions
        unanswered_row = ttk.Frame(stats_frame)
        unanswered_row.pack(fill=tk.X, pady=5)

        unanswered_label = ttk.Label(unanswered_row, text="Unanswered:", style="Field.TLabel", width=15)
        unanswered_label.pack(side=tk.LEFT)

        unanswered_value = ttk.Label(unanswered_row, text=f"{self.unanswered_count}",
                                    style="Value.TLabel", foreground="#f39c12")
        unanswered_value.pack(side=tk.LEFT)

        # Total questions
        total_row = ttk.Frame(stats_frame)
        total_row.pack(fill=tk.X, pady=5)

        total_label = ttk.Label(total_row, text="Total Questions:", style="Field.TLabel", width=15)
        total_label.pack(side=tk.LEFT)

        total_value = ttk.Label(total_row, text=f"{len(self.questions)}", style="Value.TLabel")
        total_value.pack(side=tk.LEFT)

    def create_button_section(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=30)

        # Review button (if callback provided)
        if self.on_review:
            self.review_button = ttk.Button(
                button_frame,
                text="Review Answers",
                style="Secondary.TButton",
                command=self.on_review_clicked
            )
            self.review_button.pack(side=tk.LEFT, padx=(0, 10))

        # Exit button
        self.exit_button = ttk.Button(
            button_frame,
            text="Exit Application",
            style="Action.TButton",
            command=self.on_exit_clicked
        )
        self.exit_button.pack(side=tk.RIGHT)

        # Print button (optional)
        self.print_button = ttk.Button(
            button_frame,
            text="Print Results",
            style="Secondary.TButton",
            command=self.on_print_clicked
        )
        self.print_button.pack(side=tk.RIGHT, padx=(0, 10))

    def bind_keyboard_events(self) -> None:
        """Bind keyboard shortcuts."""
        # Escape key to exit
        self.master.bind('<Escape>', lambda e: self.on_exit_clicked())

        # Ctrl+P to print
        self.master.bind('<Control-p>', lambda e: self.on_print_clicked())

        # Ctrl+R to review (if available)
        if self.on_review:
            self.master.bind('<Control-r>', lambda e: self.on_review_clicked())

    def on_review_clicked(self) -> None:
        """Handle Review button click."""
        if self.on_review:
            self.on_review()

    def on_exit_clicked(self) -> None:
        """Handle Exit button click."""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Exit Quiz",
            "Are you sure you want to exit the application?\n\nYour results have been saved.",
            icon="info"
        )

        if result:
            self.logger.info(f"Student {self.student.name} viewed results and exited application")
            if self.on_exit:
                self.on_exit()

    def on_print_clicked(self) -> None:
        """Handle Print button click."""
        try:
            # Generate printable report
            report_text = self.generate_printable_report()

            # Show print dialog (simplified - would need actual printing implementation)
            messagebox.showinfo(
                "Print Results",
                "Print functionality would be implemented here.\n\n"
                "Results have been prepared for printing."
            )

            # Log print action
            self.logger.info(f"Student {self.student.name} printed quiz results")

        except Exception as e:
            messagebox.showerror(
                "Print Error",
                f"Failed to prepare results for printing:\n{str(e)}"
            )
            self.logger.log_application_error(e, "printing results")

    def generate_printable_report(self) -> str:
        """
        Generate a printable report of the quiz results.

        Returns:
            Formatted report text
        """
        report = []
        report.append("=" * 60)
        report.append("QUIZ RESULTS REPORT")
        report.append("=" * 60)
        report.append(f"Date: {self.student.date_of_exam}")
        report.append(f"Student: {self.student.display_name}")
        report.append(f"University: {self.student.display_university}")
        report.append(f"Time Taken: {self.student.get_formatted_time_taken()}")
        report.append("")
        report.append("SCORE SUMMARY")
        report.append("-" * 30)
        report.append(f"Final Score: {self.total_achieved_marks} / {self.total_possible_marks}")
        report.append(f"Percentage: {self.percentage:.1f}%")
        report.append(f"Performance: {self.performance_level}")
        report.append("")
        report.append("ANSWER BREAKDOWN")
        report.append("-" * 30)
        report.append(f"Correct: {self.correct_count}")
        report.append(f"Incorrect: {self.incorrect_count}")
        report.append(f"Unanswered: {self.unanswered_count}")
        report.append(f"Total Questions: {len(self.questions)}")
        report.append("")
        report.append("=" * 60)

        return "\n".join(report)

    def get_detailed_answer_review(self) -> List[dict]:
        """
        Get detailed review of all answers.

        Returns:
            List of dictionaries with question and answer details
        """
        review_data = []

        for i, question in enumerate(self.questions):
            answer_data = {
                'question_number': i + 1,
                'question_text': question.question_text,
                'options': question.options,
                'correct_answer': question.correct_answer,
                'marks': question.marks,
                'difficulty': question.difficulty.value
            }

            if i < len(self.answers) and self.answers[i]:
                if self.answers[i].startswith("option"):
                    option_num = int(self.answers[i].replace("option", "")) - 1
                    selected_answer = question.get_option(option_num)
                    answer_data['student_answer'] = selected_answer
                    answer_data['is_correct'] = question.check_answer(selected_answer)
                    answer_data['answered'] = True
                else:
                    answer_data['student_answer'] = ""
                    answer_data['is_correct'] = False
                    answer_data['answered'] = False
            else:
                answer_data['student_answer'] = ""
                answer_data['is_correct'] = False
                answer_data['answered'] = False

            review_data.append(answer_data)

        return review_data

    def get_frame(self) -> ttk.Frame:
        """
        Get the main frame widget.

        Returns:
            Main results frame
        """
        return self.frame

    def show_frame(self) -> None:
        """Show the results frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self) -> None:
        """Hide the results frame."""
        self.frame.pack_forget()

    def refresh_results(self) -> None:
        """Refresh the results display (useful if data changes)."""
        self.calculate_results()
        # Would need to update all display elements here

    def get_results_summary(self) -> dict:
        """
        Get a summary of the results.

        Returns:
            Dictionary with result summary
        """
        return {
            'student_name': self.student.display_name,
            'university': self.student.display_university,
            'score': self.total_achieved_marks,
            'total_possible': self.total_possible_marks,
            'percentage': self.percentage,
            'performance_level': self.performance_level,
            'correct_count': self.correct_count,
            'incorrect_count': self.incorrect_count,
            'unanswered_count': self.unanswered_count,
            'time_taken': self.student.get_formatted_time_taken()
        }