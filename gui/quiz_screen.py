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
from quiz_config import get_config


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

        # Initialize face monitoring
        self.setup_face_monitoring()

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

        # Answer confirmation styles
        style.configure("AnswerSelected.TRadiobutton",
                       font=("Arial", 11, "bold"),
                       foreground="#27ae60")  # Green for selected

        style.configure("AnswerHover.TRadiobutton",
                       font=("Arial", 11, "underline"),
                       foreground="#3498db")  # Blue on hover

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

        # Face monitoring styles
        style.configure("FaceStatus.TLabel",
                       font=("Arial", 10, "bold"),
                       foreground="#2c3e50")

        # Help button style
        style.configure("Help.TButton",
                       font=("Arial", 10, "bold"),
                       padding=(8, 4),
                       foreground="#3498db")

        # Difficulty indicator styles
        style.configure("DifficultySimple.TLabel",
                       font=("Arial", 10, "bold"),
                       foreground="#27ae60")  # Green for simple

        style.configure("DifficultyMedium.TLabel",
                       font=("Arial", 10, "bold"),
                       foreground="#f39c12")  # Orange for medium

        style.configure("DifficultyComplex.TLabel",
                       font=("Arial", 10, "bold"),
                       foreground="#e74c3c")  # Red for complex

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

        # Help button
        self.help_button = ttk.Button(
            counter_frame,
            text="?",
            style="Help.TButton",
            command=self.show_help_overlay,
            width=3
        )
        self.help_button.pack(side=tk.RIGHT, padx=(0, 10))

        # Question and difficulty container
        question_info_frame = ttk.Frame(counter_frame)
        question_info_frame.pack(anchor=tk.W, fill=tk.X)

        self.question_counter_label = ttk.Label(
            question_info_frame,
            text="Question 1 of 10",
            style="Counter.TLabel"
        )
        self.question_counter_label.pack(side=tk.LEFT)

        # Difficulty indicator
        self.difficulty_label = ttk.Label(
            question_info_frame,
            text="",
            font=("Arial", 10, "bold")
        )
        self.difficulty_label.pack(side=tk.LEFT, padx=(10, 0))

        # Student info
        student_info_label = ttk.Label(
            counter_frame,
            text=f"Student: {self.student.display_name} | {self.student.display_university}",
            font=("Arial", 10),
            foreground="#7f8c8d"
        )
        student_info_label.pack(anchor=tk.W, pady=(5, 0))

        # Face monitoring status
        face_frame = ttk.Frame(counter_frame)
        face_frame.pack(fill=tk.X, pady=(5, 0))

        self.face_status_label = ttk.Label(
            face_frame,
            text="👁 Face Monitoring: Initializing...",
            style="FaceStatus.TLabel",
            foreground="#f39c12"
        )
        self.face_status_label.pack(side=tk.LEFT)

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
        self.option_frames = []
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
            radio.pack(anchor=tk.W, fill=tk.X)

            # Store reference to both radio and frame
            self.option_radios.append(radio)
            self.option_frames.append(option_frame)

            # Bind hover events for visual feedback
            radio.bind('<Enter>', lambda e, idx=i: self.on_option_hover(idx, True))
            radio.bind('<Leave>', lambda e, idx=i: self.on_option_hover(idx, False))

        # Bind variable change event for immediate visual feedback
        self.radio_var.trace('w', self.on_answer_changed)

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
        # Get configuration for timer duration
        config = get_config()
        timer_duration_seconds = config.quiz_duration_minutes * 60

        self.timer = QuizTimer(
            master=self.frame,
            total_seconds=timer_duration_seconds,
            time_update_callback=self.update_timer_display,
            expiration_callback=self.on_timer_expired,
            warning_callback=self.on_timer_warning
        )

    def setup_face_monitoring(self) -> None:
        """Set up face monitoring system."""
        try:
            # Get face monitoring configuration
            config = get_config()

            # Only initialize if face monitoring is enabled
            if not config.enable_face_monitoring:
                self.face_monitoring_enabled = False
                self.update_face_status("Disabled", "#95a5a6")  # Gray
                self.logger.info("Face monitoring disabled in configuration")
                return

            self.face_detector = FaceDetector(
                camera_index=config.camera_index,
                detection_interval=config.face_detection_interval,
                absence_threshold=config.face_absence_threshold,
                callback=self.on_face_detection_event
            )

            # Try to initialize camera
            if self.face_detector.test_camera():
                self.face_monitoring_enabled = True
                self.update_face_status("Ready", "#27ae60")  # Green
                self.logger.info("Face monitoring initialized successfully")
            else:
                self.face_monitoring_enabled = False
                self.update_face_status("Camera Unavailable", "#e74c3c")  # Red
                self.logger.warning("Camera not available for face monitoring")

        except Exception as e:
            self.face_monitoring_enabled = False
            self.update_face_status("Disabled", "#95a5a6")  # Gray
            self.logger.error(f"Failed to initialize face monitoring: {e}")

    def update_face_status(self, status: str, color: str = "#2c3e50") -> None:
        """
        Update the face monitoring status display.

        Args:
            status: Status text to display
            color: Text color
        """
        if hasattr(self, 'face_status_label'):
            self.face_status_label.config(
                text=f"👁 Face Monitoring: {status}",
                foreground=color
            )

    def on_face_detection_event(self, event_type: str, is_present: bool) -> None:
        """
        Handle face detection events.

        Args:
            event_type: Type of event (face_detected, user_away)
            is_present: Whether face is detected
        """
        if not self.is_quiz_active:
            return

        if event_type == "face_detected":
            if is_present:
                self.update_face_status("Present", "#27ae60")  # Green
            else:
                self.update_face_status("Looking Away", "#f39c12")  # Orange
        elif event_type == "user_away":
            self.update_face_status("AWAY", "#e74c3c")  # Red
            self.away_notifications += 1

            # Show warning for user
            self.master.after(0, self.show_away_warning)

    def show_away_warning(self) -> None:
        """Show warning when user looks away from screen."""
        if self.away_notifications <= 3:  # Only show first few warnings
            messagebox.showwarning(
                "Attention Required",
                "Please maintain focus on the quiz. Face detection indicates you're looking away from the screen."
            )
            self.logger.info(f"Away notification #{self.away_notifications} for student {self.student.name}")

    def start_quiz(self) -> None:
        """Start the quiz."""
        self.is_quiz_active = True
        self.student.start_quiz()
        self.timer.start()
        self.display_question(0)

        # Start face monitoring if enabled
        if self.face_monitoring_enabled and self.face_detector:
            if self.face_detector.start_monitoring():
                self.update_face_status("Active", "#27ae60")
                self.logger.info("Face monitoring started")
            else:
                self.update_face_status("Failed to Start", "#e74c3c")
                self.logger.error("Failed to start face monitoring")

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

        # Update difficulty indicator
        self.update_difficulty_indicator(current_question.difficulty)

        # Update options
        options = current_question.get_options_with_labels()
        for i, (label, option_text) in enumerate(options.items()):
            if i < len(self.option_radios):
                self.option_radios[i].config(text=f"{label}. {option_text}")

        # Reset option styles first
        self.reset_option_styles()

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

        # Add visual confirmation
        self.show_answer_confirmation()

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

    def on_answer_changed(self, *args) -> None:
        """Handle radio button variable changes for immediate visual feedback."""
        selected_value = self.radio_var.get()

        # Reset all radio buttons to normal style
        for i, radio in enumerate(self.option_radios):
            if selected_value == f"option{i+1}":
                # Selected option - make it green and bold
                radio.config(style="AnswerSelected.TRadiobutton")
                self.option_frames[i].config(relief=tk.RAISED, borderwidth=2, relief=tk.GROOVE)
                self.option_frames[i].config(background="#d5f4e6")  # Light green background
            else:
                # Unselected options - normal style
                radio.config(style="Quiz.TRadiobutton")
                self.option_frames[i].config(relief=tk.FLAT, borderwidth=0)
                self.option_frames[i].config(background="")  # Default background

    def on_option_hover(self, option_index: int, is_entering: bool) -> None:
        """Handle hover events on option radio buttons."""
        radio = self.option_radios[option_index]

        if is_entering:
            # Only change style if not already selected
            if self.radio_var.get() != f"option{option_index+1}":
                radio.config(style="AnswerHover.TRadiobutton")
                self.option_frames[option_index].config(background="#e8f4f8")  # Light blue background
        else:
            # Restore appropriate style when hover ends
            if self.radio_var.get() == f"option{option_index+1}":
                radio.config(style="AnswerSelected.TRadiobutton")
                self.option_frames[option_index].config(background="#d5f4e6")
            else:
                radio.config(style="Quiz.TRadiobutton")
                self.option_frames[option_index].config(background="")

    def show_answer_confirmation(self) -> None:
        """Show brief visual confirmation when answer is selected."""
        try:
            # Create a temporary confirmation label
            if hasattr(self, 'frame'):
                confirm_label = tk.Label(
                    self.frame,
                    text="✓ Answer Selected",
                    font=("Arial", 11, "bold"),
                    fg="#27ae60",
                    bg="white",
                    relief=tk.RAISED,
                    borderwidth=1,
                    padx=15,
                    pady=5
                )

                # Position it at the bottom of the screen
                confirm_label.place(relx=0.5, rely=0.92, anchor=tk.CENTER)

                # Remove after 1.5 seconds
                self.frame.after(1500, confirm_label.destroy)

        except Exception as e:
            self.logger.error(f"Failed to show answer confirmation: {e}")

    def reset_option_styles(self) -> None:
        """Reset all option styles to default."""
        for i, (radio, frame) in enumerate(zip(self.option_radios, self.option_frames)):
            radio.config(style="Quiz.TRadiobutton")
            frame.config(relief=tk.FLAT, borderwidth=0, background="")

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
        config = get_config()

        # Check if remaining time matches any configured warning times
        if remaining_seconds in config.timer_warning_times:
            if remaining_seconds >= 60:
                minutes = remaining_seconds // 60
                seconds = remaining_seconds % 60
                time_str = f"{minutes} minute{'s' if minutes != 1 else ''}"
                if seconds > 0:
                    time_str += f" {seconds} second{'s' if seconds != 1 else ''}"
            else:
                time_str = f"{remaining_seconds} second{'s' if remaining_seconds != 1 else ''}"

            messagebox.showwarning(
                "Time Warning",
                f"You have {time_str} remaining to complete the quiz!"
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

        # Stop face monitoring
        if self.face_monitoring_enabled and self.face_detector:
            self.face_detector.stop_monitoring()
            self.update_face_status("Stopped", "#95a5a6")

        self.timer.stop()
        self.student.end_quiz()
        self.student.set_answers(self.answers)

        # Calculate score
        score = self.calculate_score()

        # Update student score
        self.student.marks_scored = score

        # Log quiz completion with face monitoring stats
        face_stats = {}
        if self.face_monitoring_enabled and self.face_detector:
            face_stats = self.face_detector.get_monitoring_stats()
            self.logger.info(f"Face monitoring stats: {face_stats}")

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
        # Navigation shortcuts
        self.master.bind('<Control-Left>', lambda e: self.on_previous_clicked())
        self.master.bind('<Control-Right>', lambda e: self.on_next_clicked())
        self.master.bind('<Alt-Left>', lambda e: self.go_to_first_question())
        self.master.bind('<Alt-Right>', lambda e: self.go_to_last_question())

        # Quiz control shortcuts
        self.master.bind('<Control-Return>', lambda e: self.on_submit_clicked())
        self.master.bind('<F1>', lambda e: self.show_help_overlay())

        # Answer selection shortcuts
        for i in range(1, 5):
            self.master.bind(str(i), lambda e, num=i: self.select_answer_by_number(num))

        # Clear current answer
        self.master.bind('<space>', lambda e: self.clear_current_answer())

        # Additional shortcuts (basic implementations)
        self.master.bind('<Control-s>', lambda e: self.save_progress())
        self.master.bind('<Control-p>', lambda e: self.toggle_timer_pause())
        self.master.bind('<Control-t>', lambda e: self.show_time_remaining())

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

        # Stop face monitoring
        if self.face_monitoring_enabled and self.face_detector:
            self.face_detector.stop_monitoring()
            self.face_detector.cleanup()

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

    def show_help_overlay(self) -> None:
        """Show keyboard shortcuts help overlay."""
        help_window = tk.Toplevel(self.master)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("450x500")
        help_window.resizable(False, False)
        help_window.configure(bg="#ecf0f1")

        # Make it modal (focus stays on help window)
        help_window.transient(self.master)
        help_window.grab_set()

        # Center the help window
        help_window.update_idletasks()
        x = (help_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (help_window.winfo_screenheight() // 2) - (500 // 2)
        help_window.geometry(f"+{x}+{y}")

        # Title
        title_label = tk.Label(
            help_window,
            text="⌨️ Keyboard Shortcuts",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        title_label.pack(pady=(20, 10))

        # Subtitle
        subtitle_label = tk.Label(
            help_window,
            text="Navigate your quiz faster with these shortcuts",
            font=("Arial", 11),
            bg="#ecf0f1",
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=(0, 20))

        # Create scrollable frame for shortcuts
        canvas = tk.Canvas(help_window, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(help_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Keyboard shortcuts data
        shortcuts = [
            ("Navigation", [
                ("Ctrl + ←", "Previous Question"),
                ("Ctrl + →", "Next Question"),
                ("Alt + ←", "First Question"),
                ("Alt + →", "Last Question")
            ]),
            ("Answer Selection", [
                ("1", "Select Option A"),
                ("2", "Select Option B"),
                ("3", "Select Option C"),
                ("4", "Select Option D"),
                ("Space", "Clear Current Answer")
            ]),
            ("Quiz Control", [
                ("Ctrl + Enter", "Submit Quiz"),
                ("Ctrl + S", "Save Progress"),
                ("F1", "Show Help (This Window)"),
                ("Escape", "Close Help")
            ]),
            ("Timer Control", [
                ("Ctrl + P", "Pause/Resume Timer"),
                ("Ctrl + T", "Show Time Remaining")
            ])
        ]

        # Create shortcuts display
        for category, category_shortcuts in shortcuts:
            # Category header
            category_frame = ttk.Frame(scrollable_frame)
            category_frame.pack(fill=tk.X, padx=20, pady=(15, 5))

            category_label = tk.Label(
                category_frame,
                text=category,
                font=("Arial", 12, "bold"),
                bg="#ecf0f1",
                fg="#3498db"
            )
            category_label.pack(anchor=tk.W)

            # Category shortcuts
            for shortcut, description in category_shortcuts:
                shortcut_frame = ttk.Frame(scrollable_frame)
                shortcut_frame.pack(fill=tk.X, padx=30, pady=2)

                # Shortcut key
                shortcut_label = tk.Label(
                    shortcut_frame,
                    text=shortcut,
                    font=("Courier", 11, "bold"),
                    bg="#ecf0f1",
                    fg="#2c3e50",
                    width=12,
                    anchor=tk.W
                )
                shortcut_label.pack(side=tk.LEFT)

                # Description
                desc_label = tk.Label(
                    shortcut_frame,
                    text=description,
                    font=("Arial", 11),
                    bg="#ecf0f1",
                    fg="#34495e",
                    anchor=tk.W
                )
                desc_label.pack(side=tk.LEFT, padx=(10, 0))

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=(0, 10))
        scrollbar.pack(side="right", fill="y", pady=(0, 10))

        # Bottom frame
        bottom_frame = ttk.Frame(help_window)
        bottom_frame.pack(fill=tk.X, padx=20, pady=(10, 20))

        # Tip
        tip_label = tk.Label(
            bottom_frame,
            text="💡 Tip: Keep this window open while taking the quiz for reference",
            font=("Arial", 10, "italic"),
            bg="#ecf0f1",
            fg="#27ae60"
        )
        tip_label.pack(pady=(0, 10))

        # Close button
        close_button = ttk.Button(
            bottom_frame,
            text="Close (Escape)",
            command=help_window.destroy
        )
        close_button.pack()

        # Bind Escape key to close help
        help_window.bind('<Escape>', lambda e: help_window.destroy())

        # Center focus on close button
        close_button.focus()

        self.logger.info("Help overlay displayed")

    def go_to_first_question(self) -> None:
        """Navigate to the first question."""
        self.display_question(0)

    def go_to_last_question(self) -> None:
        """Navigate to the last question."""
        self.display_question(len(self.questions) - 1)

    def clear_current_answer(self) -> None:
        """Clear the answer for the current question."""
        self.radio_var.set("")
        self.answers[self.current_question_index] = ""
        self.update_progress_indicator()
        self.logger.info(f"Cleared answer for question {self.current_question_index + 1}")

    def save_progress(self) -> None:
        """Save current quiz progress (basic implementation)."""
        try:
            # Basic progress save - could be enhanced later
            self.logger.info(f"Progress saved - Question {self.current_question_index + 1}, {sum(1 for a in self.answers if a)}/{len(self.questions)} answered")
            # Show brief confirmation (non-intrusive)
            if hasattr(self, 'frame'):
                temp_label = tk.Label(self.frame, text="✓ Progress saved", fg="#27ae60", font=("Arial", 10))
                temp_label.place(relx=0.5, rely=0.05)
                self.frame.after(2000, temp_label.destroy)
        except Exception as e:
            self.logger.error(f"Failed to save progress: {e}")

    def toggle_timer_pause(self) -> None:
        """Toggle timer pause/resume (basic implementation)."""
        if self.timer and hasattr(self.timer, 'is_paused'):
            if not self.timer.is_paused:
                self.timer.pause()
                self.logger.info("Timer paused")
            else:
                self.timer.resume()
                self.logger.info("Timer resumed")

    def show_time_remaining(self) -> None:
        """Show time remaining in a popup."""
        if self.timer:
            remaining_seconds = self.timer.get_remaining_seconds()
            minutes = remaining_seconds // 60
            seconds = remaining_seconds % 60

            messagebox.showinfo(
                "Time Remaining",
                f"Time remaining: {minutes:02d}:{seconds:02d}\n"
                f"Current question: {self.current_question_index + 1}/{len(self.questions)}\n"
                f"Answered: {sum(1 for a in self.answers if a)}/{len(self.questions)} questions"
            )