"""
Registration Screen for Quiz Application
Handles student registration with validation and error handling.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from models.student import Student
from utils.logger import get_logger


class RegistrationScreen:
    """Registration screen for student information collection."""

    def __init__(self, master: tk.Tk,
                 on_registration_success: Optional[Callable[[Student], None]] = None,
                 on_cancel: Optional[Callable[[], None]] = None):
        """
        Initialize registration screen.

        Args:
            master: Parent tkinter window
            on_registration_success: Callback when registration succeeds
            on_cancel: Callback when user cancels registration
        """
        self.master = master
        self.on_registration_success = on_registration_success
        self.on_cancel = on_cancel
        self.logger = get_logger()

        # Create registration frame
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Configure style
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Set up validation
        self.setup_validation()

        # Bind keyboard events
        self.bind_events()

    def setup_styles(self) -> None:
        """Configure ttk styles for the registration screen."""
        style = ttk.Style()

        # Configure title style
        style.configure("Title.TLabel",
                       font=("Arial", 18, "bold"),
                       foreground="#2c3e50")

        # Configure subtitle style
        style.configure("Subtitle.TLabel",
                       font=("Arial", 12),
                       foreground="#7f8c8d")

        # Configure field label style
        style.configure("Field.TLabel",
                       font=("Arial", 10, "bold"),
                       foreground="#2c3e50")

        # Configure button style
        style.configure("Action.TButton",
                       font=("Arial", 10, "bold"),
                       padding=(20, 10))

        # Configure error label style
        style.configure("Error.TLabel",
                       font=("Arial", 9),
                       foreground="#e74c3c")

    def create_widgets(self) -> None:
        """Create all widgets for the registration screen."""
        # Main container
        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title section
        self.create_title_section(main_frame)

        # Form section
        self.create_form_section(main_frame)

        # Button section
        self.create_button_section(main_frame)

        # Error section
        self.create_error_section(main_frame)

    def create_title_section(self, parent: ttk.Frame) -> None:
        """Create title and subtitle."""
        title_frame = ttk.Frame(parent)
        title_frame.pack(fill=tk.X, pady=(0, 30))

        # Main title
        title_label = ttk.Label(
            title_frame,
            text="Quiz Application",
            style="Title.TLabel"
        )
        title_label.pack()

        # Subtitle
        subtitle_label = ttk.Label(
            title_frame,
            text="Please register to begin the quiz",
            style="Subtitle.TLabel"
        )
        subtitle_label.pack(pady=(5, 0))

    def create_form_section(self, parent: ttk.Frame) -> None:
        """Create the registration form."""
        form_frame = ttk.Frame(parent)
        form_frame.pack(fill=tk.X, pady=20)

        # Name field
        name_frame = ttk.Frame(form_frame)
        name_frame.pack(fill=tk.X, pady=10)

        name_label = ttk.Label(
            name_frame,
            text="Full Name:",
            style="Field.TLabel"
        )
        name_label.pack(anchor=tk.W)

        self.name_entry = ttk.Entry(
            name_frame,
            font=("Arial", 11),
            width=40
        )
        self.name_entry.pack(fill=tk.X, pady=(5, 0))
        self.name_entry.focus_set()

        # University field
        university_frame = ttk.Frame(form_frame)
        university_frame.pack(fill=tk.X, pady=10)

        university_label = ttk.Label(
            university_frame,
            text="University:",
            style="Field.TLabel"
        )
        university_label.pack(anchor=tk.W)

        self.university_entry = ttk.Entry(
            university_frame,
            font=("Arial", 11),
            width=40
        )
        self.university_entry.pack(fill=tk.X, pady=(5, 0))

        # Add hint text
        hint_label = ttk.Label(
            form_frame,
            text="Note: Both fields are required and must contain valid information",
            font=("Arial", 9),
            foreground="#95a5a6"
        )
        hint_label.pack(pady=(15, 0))

    def create_button_section(self, parent: ttk.Frame) -> None:
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=20)

        # OK button
        self.ok_button = ttk.Button(
            button_frame,
            text="Start Quiz",
            style="Action.TButton",
            command=self.on_ok_clicked
        )
        self.ok_button.pack(side=tk.RIGHT, padx=(10, 0))

        # Cancel button
        self.cancel_button = ttk.Button(
            button_frame,
            text="Cancel",
            command=self.on_cancel_clicked
        )
        self.cancel_button.pack(side=tk.RIGHT)

    def create_error_section(self, parent: ttk.Frame) -> None:
        """Create error message display area."""
        error_frame = ttk.Frame(parent)
        error_frame.pack(fill=tk.X, pady=10)

        self.error_label = ttk.Label(
            error_frame,
            text="",
            style="Error.TLabel",
            wraplength=400
        )
        self.error_label.pack()

    def setup_validation(self) -> None:
        """Set up input validation."""
        # Name validation
        name_validate_cmd = (self.master.register(self.validate_name_input), '%P')
        self.name_entry.config(validate="key", validatecommand=name_validate_cmd)

        # University validation
        university_validate_cmd = (self.master.register(self.validate_university_input), '%P')
        self.university_entry.config(validate="key", validatecommand=university_validate_cmd)

    def bind_events(self) -> None:
        """Bind keyboard events."""
        # Enter key to submit
        self.master.bind('<Return>', lambda e: self.on_ok_clicked())

        # Escape key to cancel
        self.master.bind('<Escape>', lambda e: self.on_cancel_clicked())

        # Tab navigation
        self.name_entry.bind('<Tab>', self.on_tab_pressed)
        self.university_entry.bind('<Shift-Tab>', self.on_shift_tab_pressed)

    def validate_name_input(self, value: str) -> bool:
        """
        Validate name input in real-time.

        Args:
            value: Current input value

        Returns:
            True if input is valid so far
        """
        # Allow empty input (user is still typing)
        if not value:
            return True

        # Check length
        if len(value) > 50:
            return False

        # Allow only letters, spaces, hyphens, apostrophes, and periods
        import re
        if not re.match(r'^[a-zA-Z\s\-\'\.]*$', value):
            return False

        return True

    def validate_university_input(self, value: str) -> bool:
        """
        Validate university input in real-time.

        Args:
            value: Current input value

        Returns:
            True if input is valid so far
        """
        # Allow empty input (user is still typing)
        if not value:
            return True

        # Check length
        if len(value) > 100:
            return False

        # Allow only letters, numbers, spaces, and common punctuation
        import re
        if not re.match(r'^[a-zA-Z0-9\s\-\.,\'&]*$', value):
            return False

        return True

    def on_tab_pressed(self, event) -> None:
        """Handle Tab key press."""
        if self.master.focus_get() == self.name_entry:
            self.university_entry.focus_set()
            return "break"
        return event

    def on_shift_tab_pressed(self, event) -> None:
        """Handle Shift+Tab key press."""
        if self.master.focus_get() == self.university_entry:
            self.name_entry.focus_set()
            return "break"
        return event

    def get_form_data(self) -> tuple[str, str]:
        """
        Get current form data.

        Returns:
            Tuple of (name, university)
        """
        name = self.name_entry.get().strip()
        university = self.university_entry.get().strip()
        return name, university

    def validate_form(self) -> tuple[bool, list]:
        """
        Validate the complete form.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        name, university = self.get_form_data()

        # Create student object for validation
        student = Student(name=name, university=university)
        return student.validate()

    def show_error(self, message: str) -> None:
        """
        Display error message.

        Args:
            message: Error message to display
        """
        self.error_label.config(text=message)
        self.logger.log_validation_error("Registration", "", message)

    def clear_error(self) -> None:
        """Clear error message."""
        self.error_label.config(text="")

    def on_ok_clicked(self) -> None:
        """Handle OK button click."""
        self.clear_error()

        # Get form data
        name, university = self.get_form_data()

        # Validate form
        is_valid, errors = self.validate_form()

        if not is_valid:
            self.show_error("\n".join(errors))
            return

        # Create student object
        student = Student(name=name, university=university)

        # Log registration attempt
        self.logger.info(f"Registration attempt: {name} from {university}")

        # Call success callback
        if self.on_registration_success:
            self.on_registration_success(student)

    def on_cancel_clicked(self) -> None:
        """Handle Cancel button click."""
        # Show confirmation dialog
        result = messagebox.askyesno(
            "Cancel Registration",
            "Are you sure you want to exit the quiz application?",
            icon="warning"
        )

        if result:
            self.logger.info("User cancelled registration")
            if self.on_cancel:
                self.on_cancel()

    def clear_form(self) -> None:
        """Clear all form fields."""
        self.name_entry.delete(0, tk.END)
        self.university_entry.delete(0, tk.END)
        self.clear_error()
        self.name_entry.focus_set()

    def set_field_values(self, name: str = "", university: str = "") -> None:
        """
        Set field values (for testing or pre-filling).

        Args:
            name: Name to set
            university: University to set
        """
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, name)

        self.university_entry.delete(0, tk.END)
        self.university_entry.insert(0, university)

        self.clear_error()

    def get_frame(self) -> ttk.Frame:
        """
        Get the main frame widget.

        Returns:
            Main registration frame
        """
        return self.frame

    def show_frame(self) -> None:
        """Show the registration frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self) -> None:
        """Hide the registration frame."""
        self.frame.pack_forget()

    def set_focus_to_name(self) -> None:
        """Set focus to name field."""
        self.name_entry.focus_set()

    def set_focus_to_university(self) -> None:
        """Set focus to university field."""
        self.university_entry.focus_set()

    def enable_form(self) -> None:
        """Enable all form controls."""
        self.name_entry.config(state="normal")
        self.university_entry.config(state="normal")
        self.ok_button.config(state="normal")
        self.cancel_button.config(state="normal")

    def disable_form(self) -> None:
        """Disable all form controls."""
        self.name_entry.config(state="disabled")
        self.university_entry.config(state="disabled")
        self.ok_button.config(state="disabled")
        self.cancel_button.config(state="disabled")

    def set_processing_state(self, processing: bool) -> None:
        """
        Set processing state (show/hide loading indicator).

        Args:
            processing: Whether the form is in processing state
        """
        if processing:
            self.ok_button.config(text="Processing...", state="disabled")
            self.disable_form()
        else:
            self.ok_button.config(text="Start Quiz", state="normal")
            self.enable_form()