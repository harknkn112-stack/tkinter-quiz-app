"""
Timer Utility for Quiz Application
Manages countdown timer and automatic submission functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from datetime import datetime, timedelta
import threading


class QuizTimer:
    """Manages countdown timer for quiz with automatic submission support."""

    def __init__(self, master: tk.Widget, total_seconds: int = 600,
                 time_update_callback: Optional[Callable[[str], None]] = None,
                 expiration_callback: Optional[Callable[[], None]] = None,
                 warning_callback: Optional[Callable[[int], None]] = None):
        """
        Initialize the quiz timer.

        Args:
            master: Parent tkinter widget
            total_seconds: Total time for quiz in seconds (default: 600 = 10 minutes)
            time_update_callback: Callback function called every second with formatted time
            expiration_callback: Callback function called when timer expires
            warning_callback: Callback function called at specific warning intervals
        """
        self.master = master
        self.total_seconds = total_seconds
        self.remaining_seconds = total_seconds
        self.time_update_callback = time_update_callback
        self.expiration_callback = expiration_callback
        self.warning_callback = warning_callback

        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = None
        self.pause_duration = 0

        # Warning times (in seconds)
        self.warning_times = [120, 60, 30, 10]  # 2 min, 1 min, 30 sec, 10 sec
        self.triggered_warnings = set()

        # Timer display label
        self.timer_label = None
        self.setup_timer_display()

        # Track time for submission
        self.actual_time_taken = 0

    def setup_timer_display(self) -> None:
        """Set up the timer display widget."""
        style = ttk.Style()
        style.configure("Timer.TLabel",
                       font=("Arial", 16, "bold"),
                       background="white",
                       foreground="black")

        self.timer_label = ttk.Label(
            self.master,
            text=self.format_time(self.remaining_seconds),
            style="Timer.TLabel"
        )

    def get_timer_widget(self) -> ttk.Label:
        """
        Get the timer display widget.

        Returns:
            Timer label widget
        """
        return self.timer_label

    def start(self) -> None:
        """Start the countdown timer."""
        if not self.is_running:
            self.is_running = True
            self.is_paused = False
            self.start_time = datetime.now()
            self.actual_time_taken = 0
            self.update_display()
            self.schedule_update()

    def pause(self) -> None:
        """Pause the timer (for testing purposes)."""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.pause_time = datetime.now()

    def resume(self) -> None:
        """Resume the timer from pause."""
        if self.is_running and self.is_paused:
            if self.pause_time:
                self.pause_duration += (datetime.now() - self.pause_time).total_seconds()
            self.is_paused = False
            self.pause_time = None
            self.update_display()
            self.schedule_update()

    def stop(self) -> None:
        """Stop the timer and record actual time taken."""
        self.is_running = False
        if self.start_time:
            end_time = datetime.now()
            self.actual_time_taken = int((end_time - self.start_time).total_seconds() - self.pause_duration)

    def reset(self, total_seconds: Optional[int] = None) -> None:
        """
        Reset the timer to initial state.

        Args:
            total_seconds: New total time in seconds (optional)
        """
        if total_seconds is not None:
            self.total_seconds = total_seconds

        self.remaining_seconds = self.total_seconds
        self.is_running = False
        self.is_paused = False
        self.start_time = None
        self.pause_time = None
        self.pause_duration = 0
        self.actual_time_taken = 0
        self.triggered_warnings.clear()
        self.update_display()

    def schedule_update(self) -> None:
        """Schedule the next timer update using tkinter's after method."""
        if self.is_running and not self.is_paused:
            self.master.after(1000, self.update_timer)

    def update_timer(self) -> None:
        """Update the timer every second."""
        if self.is_running and not self.is_paused:
            self.remaining_seconds -= 1

            # Update display
            self.update_display()

            # Check for warnings
            self.check_warnings()

            # Check for expiration
            if self.remaining_seconds <= 0:
                self.timer_expired()
            else:
                # Schedule next update
                self.schedule_update()

    def update_display(self) -> None:
        """Update the timer display and call callback."""
        formatted_time = self.format_time(self.remaining_seconds)

        if self.timer_label:
            # Change color when time is running out
            if self.remaining_seconds <= 60:  # Last minute
                self.timer_label.configure(foreground="red")
            elif self.remaining_seconds <= 120:  # Last 2 minutes
                self.timer_label.configure(foreground="orange")
            else:
                self.timer_label.configure(foreground="black")

            self.timer_label.configure(text=formatted_time)

        # Call callback if provided
        if self.time_update_callback:
            self.time_update_callback(formatted_time)

    def check_warnings(self) -> None:
        """Check and trigger time warnings."""
        if self.warning_callback:
            for warning_time in self.warning_times:
                if (self.remaining_seconds == warning_time and
                    warning_time not in self.triggered_warnings):
                    self.warning_callback(self.remaining_seconds)
                    self.triggered_warnings.add(warning_time)

    def timer_expired(self) -> None:
        """Handle timer expiration."""
        self.remaining_seconds = 0
        self.is_running = False
        self.actual_time_taken = self.total_seconds

        # Update display one last time
        self.update_display()

        # Log timer expiration
        from .logger import get_logger
        get_logger().log_timer_event("Timer expired", "00:00")

        # Call expiration callback
        if self.expiration_callback:
            self.expiration_callback()

    def format_time(self, seconds: int) -> str:
        """
        Format seconds into MM:SS display format.

        Args:
            seconds: Number of seconds

        Returns:
            Formatted time string (MM:SS)
        """
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"

    def get_remaining_seconds(self) -> int:
        """
        Get remaining time in seconds.

        Returns:
            Remaining seconds
        """
        return self.remaining_seconds

    def get_remaining_minutes(self) -> int:
        """
        Get remaining time in minutes.

        Returns:
            Remaining minutes (rounded down)
        """
        return self.remaining_seconds // 60

    def get_time_taken(self) -> int:
        """
        Get actual time taken for quiz.

        Returns:
            Time taken in seconds
        """
        if self.is_running and self.start_time:
            # Calculate current time taken
            current_time = datetime.now()
            time_taken = int((current_time - self.start_time).total_seconds() - self.pause_duration)
            return min(time_taken, self.total_seconds)
        return self.actual_time_taken

    def is_expired(self) -> bool:
        """
        Check if timer has expired.

        Returns:
            True if timer has expired
        """
        return self.remaining_seconds <= 0

    def add_time(self, seconds: int) -> None:
        """
        Add time to the timer (for testing or special cases).

        Args:
            seconds: Number of seconds to add
        """
        self.remaining_seconds += seconds
        if self.remaining_seconds > self.total_seconds:
            self.total_seconds = self.remaining_seconds
        self.update_display()

    def set_custom_warning_times(self, warning_times: list) -> None:
        """
        Set custom warning times.

        Args:
            warning_times: List of warning times in seconds
        """
        self.warning_times = sorted(warning_times, reverse=True)
        self.triggered_warnings.clear()

    def get_time_statistics(self) -> dict:
        """
        Get timer statistics.

        Returns:
            Dictionary with timer statistics
        """
        return {
            'total_time': self.total_seconds,
            'remaining_time': self.remaining_seconds,
            'time_taken': self.get_time_taken(),
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'is_expired': self.is_expired(),
            'start_time': self.start_time,
            'pause_duration': self.pause_duration
        }

    def create_timer_frame(self, parent: tk.Widget) -> tk.Frame:
        """
        Create a frame containing the timer and a label.

        Args:
            parent: Parent widget

        Returns:
            Frame containing timer display
        """
        frame = tk.Frame(parent, bg="white", relief=tk.RIDGE, borderwidth=2)

        # Timer title
        title_label = ttk.Label(
            frame,
            text="Time Remaining:",
            font=("Arial", 10, "normal")
        )
        title_label.pack(pady=(5, 0))

        # Timer display
        self.setup_timer_display()
        self.timer_label.pack(pady=(0, 5))

        return frame

    def set_warning_colors(self, colors: dict) -> None:
        """
        Set custom warning colors for timer display.

        Args:
            colors: Dictionary with time thresholds and colors
                   Example: {60: "red", 120: "orange", 300: "yellow"}
        """
        self.warning_colors = colors

    def apply_warning_colors(self) -> None:
        """Apply warning colors based on remaining time."""
        if hasattr(self, 'warning_colors') and self.timer_label:
            color = "black"  # Default color
            for threshold, warn_color in sorted(self.warning_colors.items()):
                if self.remaining_seconds <= threshold:
                    color = warn_color
                    break
            self.timer_label.configure(foreground=color)