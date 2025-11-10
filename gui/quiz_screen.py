"""
Quiz Screen for Quiz Application
Handles question display, answer selection, navigation, and timer management.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from models.question import Question
from models.student import Student
from utils.timer import QuizTimer
from utils.logger import get_logger
from utils.face_detector import FaceDetector


class QuizScreen:
    """Main quiz interface for displaying questions and collecting answers."""

    def __init__(self, master: tk.Tk,
                 questions: List[Question],
                 student: Student,
                 on_quiz_complete: Optional[Callable[[Student, List[str]], None]] = None,
                 on_quiz_cancel: Optional[Callable[[], None]] = None):
        """
        Initialize quiz screen.

        Args:
            master: Parent tkinter window
            questions: List of questions for the quiz
            student: Student object taking the quiz
            on_quiz_complete: Callback when quiz is completed
            on_quiz_cancel: Callback when quiz is cancelled
        """
        self.master = master
        self.questions = questions
        self.student = student
        self.on_quiz_complete = on_quiz_complete
        self.on_quiz_cancel = on_quiz_cancel
        self.logger = get_logger()

        # Quiz state
        self.current_question_index = 0
        self.answers = [""] * len(questions)  # Initialize empty answers
        self.is_quiz_active = False
        self.timer_expired = False

        # Face monitoring
        self.face_detector = None
        self.face_monitoring_enabled = False
        self.away_notifications = 0

        # Create quiz frame
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Configure styles
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Initialize timer
        self.setup_timer()

        # Start the quiz
        self.start_quiz()

    def setup_styles(self) -> None:
        """Configure ttk styles for the quiz screen."""
        style = ttk.Style()

        # Timer style
        style.configure("Timer.TLabel",
                       font=("Arial", 16, "bold"),
                       background="white",
                       foreground="black")

        # Question counter style
        style.configure("Counter.TLabel",
                       font=("Arial", 11, "bold"),
                       foreground="#2c3e50")

        # Question text style
        style.configure("Question.TLabel",
                       font=("Arial", 12),
                       foreground="#2c3e50",
                       wraplength=600)

        # Option radio button style
        style.configure("Quiz.TRadiobutton",
                       font=("Arial", 11))

        # Button styles
        style.configure("Nav.TButton",
                       font=("Arial", 10, "bold"),
                       padding=(15, 8))

        style.configure("Submit.TButton",
                       font=("Arial", 11, "bold"),
                       padding=(20, 10),
                       foreground="#27ae60")

        # Progress indicator style
        style.configure("Progress.TLabel",
                       font=("Arial", 9),
                       foreground="#7f8c8d")

    def create_widgets(self) -> None:
        """Create all widgets for the quiz screen."""
        # Main container with top and bottom sections
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top section (Timer and Question Counter)
        self.create_top_section(main_container)

        # Middle section (Question and Options)
        self.create_middle_section(main_container)

        # Bottom section (Navigation and Progress)
        self.create_bottom_section(main_container)

    def create_top_section(self, parent: ttk.Frame) -> None:
        """Create timer and question counter section."""
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 20))

        # Timer container
        timer_container = ttk.Frame(top_frame, relief=tk.RIDGE, borderwidth=2)
        timer_container.pack(side=tk.RIGHT, padx=(0, 10))

        # Timer label
        self.timer_label = ttk.Label(
            timer_container,
            text="10:00",
            style="Timer.TLabel",
            padding="10"
        )
        self.timer_label.pack()

        # Question counter
        counter_frame = ttk.Frame(top_frame)
        counter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.question_counter_label = ttk.Label(
            counter_frame,
            text="Question 1 of 10",
            style="Counter.TLabel"
        )
        self.question_counter_label.pack(anchor=tk.W)

        # Student info
        student_info_label = ttk.Label(
            counter_frame,
            text=f"Student: {self.student.display_name} | {self.student.display_university}",
            font=("Arial", 10),
            foreground="#7f8c8d"
        )
        student_info_label.pack(anchor=tk.W, pady=(5, 0))

    def create_middle_section(self, parent: ttk.Frame) -> None:
        """Create question and options section."""
        middle_frame = ttk.Frame(parent)
        middle_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        # Question frame
        question_frame = ttk.Frame(middle_frame)
        question_frame.pack(fill=tk.X, pady=(0, 20))

        self.question_label = ttk.Label(
            question_frame,
            text="",
            style="Question.TLabel",
            justify=tk.LEFT
        )
        self.question_label.pack(anchor=tk.W)

        # Options frame
        options_frame = ttk.Frame(middle_frame)
        options_frame.pack(fill=tk.BOTH, expand=True)

        # Radio button variable
        self.radio_var = tk.StringVar()

        # Create radio buttons for options
        self.option_radios = []
        for i in range(4):
            option_frame = ttk.Frame(options_frame)
            option_frame.pack(fill=tk.X, pady=5)

            radio = ttk.Radiobutton(
                option_frame,
                text="",
                variable=self.radio_var,
                value=f"option{i+1}",
                style="Quiz.TRadiobutton",
                command=self.on_answer_selected
            )
            radio.pack(anchor=tk.W)
            self.option_radios.append(radio)

    def create_bottom_section(self, parent: ttk.Frame) -> None:
        """Create navigation and progress section."""
        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill=tk.X, pady=(20, 0))

        # Progress indicator
        self.create_progress_indicator(bottom_frame)

        # Navigation buttons
        self.create_navigation_buttons(bottom_frame)

    def create_progress_indicator(self, parent: ttk.Frame) -> None:
        """Create progress indicator showing question status."""
        progress_frame = ttk.Frame(parent)
        progress_frame.pack(fill=tk.X, pady=(0, 15))

        progress_label = ttk.Label(
            progress_frame,
            text="Progress: ",
            font=("Arial", 10),
            foreground="#2c3e50"
        )
        progress_label.pack(side=tk.LEFT)

        # Create question indicators
        self.progress_labels = []
        for i in range(len(self.questions)):
            label_text = f"Q{i+1}"
            label = ttk.Label(
                progress_frame,
                text=label_text,
                font=("Arial", 9, "bold"),
                foreground="#bdc3c7",
                padding=(8, 4)
            )
            label.pack(side=tk.LEFT, padx=(0, 5))
            self.progress_labels.append(label)

    def create_navigation_buttons(self, parent: ttk.Frame) -> None:
        """Create navigation buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)

        # Previous button
        self.previous_button = ttk.Button(
            button_frame,
            text="← Previous",
            style="Nav.TButton",
            command=self.on_previous_clicked
        )
        self.previous_button.pack(side=tk.LEFT)

        # Submit button
        self.submit_button = ttk.Button(
            button_frame,
            text="End Exam",
            style="Submit.TButton",
            command=self.on_submit_clicked
        )
        self.submit_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Next button
        self.next_button = ttk.Button(
            button_frame,
            text="Next →",
            style="Nav.TButton",
            command=self.on_next_clicked
        )
        self.next_button.pack(side=tk.RIGHT)

    def setup_timer(self) -> None:
        """Set up the quiz timer."""
        self.timer = QuizTimer(
            master=self.frame,
            total_seconds=600,  # 10 minutes
            time_update_callback=self.update_timer_display,
            expiration_callback=self.on_timer_expired,
            warning_callback=self.on_timer_warning
        )

    def start_quiz(self) -> None:
        """Start the quiz."""
        self.is_quiz_active = True
        self.student.start_quiz()
        self.timer.start()
        self.display_question(0)

        # Log quiz start
        self.logger.log_quiz_start(self.student.name, self.student.usn)

        # Bind keyboard events
        self.bind_keyboard_events()

    def display_question(self, question_index: int) -> None:
        """
        Display a specific question.

        Args:
            question_index: Index of question to display
        """
        if not (0 <= question_index < len(self.questions)):
            return

        self.current_question_index = question_index
        current_question = self.questions[question_index]

        # Update question counter
        self.question_counter_label.config(
            text=f"Question {question_index + 1} of {len(self.questions)}"
        )

        # Update question text
        self.question_label.config(text=current_question.question_text)

        # Update options
        options = current_question.get_options_with_labels()
        for i, (label, option_text) in enumerate(options.items()):
            if i < len(self.option_radios):
                self.option_radios[i].config(text=f"{label}. {option_text}")

        # Set selected answer if previously answered
        saved_answer = self.answers[question_index]
        if saved_answer:
            self.radio_var.set(saved_answer)
        else:
            self.radio_var.set("")  # Clear selection

        # Update navigation buttons
        self.update_navigation_buttons()

        # Update progress indicator
        self.update_progress_indicator()

        # Log question navigation
        self.logger.log_question_navigation(self.student.usn, question_index + 1)

    def update_navigation_buttons(self) -> None:
        """Update navigation button states."""
        # Disable Previous button on first question
        if self.current_question_index == 0:
            self.previous_button.config(state="disabled")
        else:
            self.previous_button.config(state="normal")

        # Disable Next button on last question
        if self.current_question_index == len(self.questions) - 1:
            self.next_button.config(state="disabled")
        else:
            self.next_button.config(state="normal")

    def update_progress_indicator(self) -> None:
        """Update progress indicator colors based on answer status."""
        for i, label in enumerate(self.progress_labels):
            if self.answers[i]:  # Question answered
                label.config(foreground="#27ae60")  # Green
            elif i == self.current_question_index:  # Current question
                label.config(foreground="#3498db")  # Blue
            else:  # Unanswered question
                label.config(foreground="#bdc3c7")  # Gray

    def on_answer_selected(self) -> None:
        """Handle answer selection."""
        selected_value = self.radio_var.get()
        self.answers[self.current_question_index] = selected_value

        # Update progress indicator
        self.update_progress_indicator()

        # Log answer selection
        current_question = self.questions[self.current_question_index]
        selected_text = ""
        if selected_value.startswith("option"):
            option_num = int(selected_value.replace("option", "")) - 1
            selected_text = current_question.get_option(option_num)

        self.logger.log_answer_selection(
            self.student.usn,
            self.current_question_index + 1,
            selected_text
        )

    def on_previous_clicked(self) -> None:
        """Handle Previous button click."""
        if self.current_question_index > 0:
            self.display_question(self.current_question_index - 1)

    def on_next_clicked(self) -> None:
        """Handle Next button click."""
        if self.current_question_index < len(self.questions) - 1:
            self.display_question(self.current_question_index + 1)

    def on_submit_clicked(self) -> None:
        """Handle Submit button click."""
        # Count answered questions
        answered_count = sum(1 for answer in self.answers if answer)

        if answered_count < len(self.questions):
            # Show warning if not all questions are answered
            result = messagebox.askyesno(
                "Incomplete Quiz",
                f"You have answered {answered_count} out of {len(self.questions)} questions.\n\n"
                "Are you sure you want to submit the quiz?",
                icon="warning"
            )
            if not result:
                return

        self.submit_quiz()

    def on_timer_expired(self) -> None:
        """Handle timer expiration."""
        self.timer_expired = True
        messagebox.showinfo(
            "Time's Up!",
            "The quiz time has expired. Your answers will be submitted automatically."
        )
        self.submit_quiz()

    def on_timer_warning(self, remaining_seconds: int) -> None:
        """Handle timer warnings."""
        if remaining_seconds == 120:  # 2 minutes
            messagebox.showwarning(
                "Time Warning",
                "You have 2 minutes remaining to complete the quiz."
            )
        elif remaining_seconds == 60:  # 1 minute
            messagebox.showwarning(
                "Time Warning",
                "You have 1 minute remaining to complete the quiz."
            )
        elif remaining_seconds == 30:  # 30 seconds
            messagebox.showwarning(
                "Time Warning",
                "You have 30 seconds remaining to complete the quiz!"
            )

    def update_timer_display(self, time_str: str) -> None:
        """
        Update timer display.

        Args:
            time_str: Formatted time string
        """
        self.timer_label.config(text=time_str)

        # Update color based on remaining time
        remaining_seconds = self.timer.get_remaining_seconds()
        if remaining_seconds <= 60:  # Last minute - red
            self.timer_label.config(foreground="#e74c3c")
        elif remaining_seconds <= 120:  # Last 2 minutes - orange
            self.timer_label.config(foreground="#f39c12")
        else:  # Normal - black
            self.timer_label.config(foreground="#2c3e50")

    def submit_quiz(self) -> None:
        """Submit the quiz and calculate results."""
        if not self.is_quiz_active:
            return

        self.is_quiz_active = False
        self.timer.stop()
        self.student.end_quiz()
        self.student.set_answers(self.answers)

        # Calculate score
        score = self.calculate_score()

        # Update student score
        self.student.marks_scored = score

        # Log quiz completion
        if self.timer_expired:
            self.logger.log_automatic_submission(
                self.student.name,
                self.student.usn,
                score
            )
        else:
            self.logger.log_manual_submission(
                self.student.name,
                self.student.usn,
                score,
                self.student.get_formatted_time_taken()
            )

        # Call completion callback
        if self.on_quiz_complete:
            self.on_quiz_complete(self.student, self.answers)

    def calculate_score(self) -> int:
        """
        Calculate the total score.

        Returns:
            Total score achieved
        """
        total_score = 0
        for i, question in enumerate(self.questions):
            if i < len(self.answers) and self.answers[i]:
                # Convert radio value to actual answer text
                if self.answers[i].startswith("option"):
                    option_num = int(self.answers[i].replace("option", "")) - 1
                    selected_answer = question.get_option(option_num)
                    if question.check_answer(selected_answer):
                        total_score += question.marks

        return total_score

    def bind_keyboard_events(self) -> None:
        """Bind keyboard shortcuts."""
        # Ctrl+Left arrow for Previous
        self.master.bind('<Control-Left>', lambda e: self.on_previous_clicked())

        # Ctrl+Right arrow for Next
        self.master.bind('<Control-Right>', lambda e: self.on_next_clicked())

        # Ctrl+Enter for Submit
        self.master.bind('<Control-Return>', lambda e: self.on_submit_clicked())

        # Number keys 1-4 for quick answer selection
        for i in range(1, 5):
            self.master.bind(str(i), lambda e, num=i: self.select_answer_by_number(num))

    def select_answer_by_number(self, number: int) -> None:
        """
        Select answer by number key (1-4).

        Args:
            number: Answer number (1-4)
        """
        if 1 <= number <= 4:
            self.radio_var.set(f"option{number}")
            self.on_answer_selected()

    def get_frame(self) -> ttk.Frame:
        """
        Get the main frame widget.

        Returns:
            Main quiz frame
        """
        return self.frame

    def show_frame(self) -> None:
        """Show the quiz frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self) -> None:
        """Hide the quiz frame."""
        self.frame.pack_forget()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.timer:
            self.timer.stop()

    def get_quiz_statistics(self) -> dict:
        """
        Get quiz statistics.

        Returns:
            Dictionary with quiz statistics
        """
        answered_count = sum(1 for answer in self.answers if answer)
        return {
            'total_questions': len(self.questions),
            'answered_questions': answered_count,
            'unanswered_questions': len(self.questions) - answered_count,
            'current_question': self.current_question_index + 1,
            'time_taken': self.timer.get_time_taken() if self.timer else 0,
            'is_active': self.is_quiz_active
        }