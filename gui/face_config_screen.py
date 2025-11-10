"""
Face Detection Configuration Screen
Allows users to configure face monitoring settings and test their camera.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable
from utils.face_detector import FaceDetector
from utils.logger import get_logger


class FaceConfigScreen:
    """Configuration screen for face detection settings."""

    def __init__(self, master: tk.Tk,
                 on_back: Optional[Callable[[], None]] = None,
                 on_save: Optional[Callable[[dict], None]] = None):
        """
        Initialize face configuration screen.

        Args:
            master: Parent tkinter window
            on_back: Callback when user goes back
            on_save: Callback when settings are saved
        """
        self.master = master
        self.on_back = on_back
        self.on_save = on_save
        self.logger = get_logger()

        # Configuration settings
        self.settings = {
            'camera_index': 0,
            'detection_interval': 1.0,
            'absence_threshold': 3,
            'enable_monitoring': True
        }

        # Face detector for testing
        self.test_detector = None

        # Create configuration frame
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # Configure styles
        self.setup_styles()

        # Create widgets
        self.create_widgets()

        # Load settings
        self.load_settings()

    def setup_styles(self) -> None:
        """Configure ttk styles."""
        style = ttk.Style()

        # Title style
        style.configure("Title.TLabel",
                       font=("Arial", 18, "bold"),
                       foreground="#2c3e50")

        # Section header style
        style.configure("Section.TLabel",
                       font=("Arial", 12, "bold"),
                       foreground="#34495e")

        # Status style
        style.configure("Status.TLabel",
                       font=("Arial", 10),
                       foreground="#7f8c8d")

    def create_widgets(self) -> None:
        """Create all widgets."""
        # Title
        title_label = ttk.Label(
            self.frame,
            text="Face Detection Configuration",
            style="Title.TLabel"
        )
        title_label.pack(pady=(0, 30))

        # Main container
        main_container = ttk.Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Camera settings section
        self.create_camera_section(main_container)

        # Detection settings section
        self.create_detection_section(main_container)

        # Test section
        self.create_test_section(main_container)

        # Button section
        self.create_button_section(main_container)

    def create_camera_section(self, parent: ttk.Frame) -> None:
        """Create camera configuration section."""
        camera_frame = ttk.LabelFrame(parent, text="Camera Settings", padding="20")
        camera_frame.pack(fill=tk.X, pady=(0, 20))

        # Camera selection
        camera_row = ttk.Frame(camera_frame)
        camera_row.pack(fill=tk.X, pady=10)

        ttk.Label(camera_row, text="Camera:", width=15).pack(side=tk.LEFT)

        self.camera_var = tk.IntVar(value=0)
        self.camera_combo = ttk.Combobox(camera_row, textvariable=self.camera_var, width=20)
        self.camera_combo.pack(side=tk.LEFT, padx=(10, 0))

        # Test camera button
        ttk.Button(camera_row, text="Test Camera", command=self.test_camera).pack(side=tk.RIGHT, padx=(10, 0))

        # Camera status
        self.camera_status_label = ttk.Label(camera_frame, text="Status: Not tested", style="Status.TLabel")
        self.camera_status_label.pack(pady=(5, 0))

        # Populate available cameras
        self.populate_cameras()

    def create_detection_section(self, parent: ttk.Frame) -> None:
        """Create detection configuration section."""
        detection_frame = ttk.LabelFrame(parent, text="Detection Settings", padding="20")
        detection_frame.pack(fill=tk.X, pady=(0, 20))

        # Enable monitoring
        enable_row = ttk.Frame(detection_frame)
        enable_row.pack(fill=tk.X, pady=10)

        self.enable_var = tk.BooleanVar(value=True)
        enable_check = ttk.Checkbutton(
            enable_row,
            text="Enable Face Monitoring During Quiz",
            variable=self.enable_var
        )
        enable_check.pack(side=tk.LEFT)

        # Detection interval
        interval_row = ttk.Frame(detection_frame)
        interval_row.pack(fill=tk.X, pady=10)

        ttk.Label(interval_row, text="Detection Interval (seconds):", width=25).pack(side=tk.LEFT)

        self.interval_var = tk.DoubleVar(value=1.0)
        interval_spinbox = ttk.Spinbox(interval_row, from_=0.5, to=5.0, increment=0.5, textvariable=self.interval_var, width=10)
        interval_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(interval_row, text="How often to check for face presence", style="Status.TLabel").pack(side=tk.LEFT, padx=(10, 0))

        # Absence threshold
        threshold_row = ttk.Frame(detection_frame)
        threshold_row.pack(fill=tk.X, pady=10)

        ttk.Label(threshold_row, text="Away Threshold:", width=25).pack(side=tk.LEFT)

        self.threshold_var = tk.IntVar(value=3)
        threshold_spinbox = ttk.Spinbox(threshold_row, from_=1, to=10, textvariable=self.threshold_var, width=10)
        threshold_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(threshold_row, text="Consecutive misses before marking as away", style="Status.TLabel").pack(side=tk.LEFT, padx=(10, 0))

    def create_test_section(self, parent: ttk.Frame) -> None:
        """Create face detection test section."""
        test_frame = ttk.LabelFrame(parent, text="Face Detection Test", padding="20")
        test_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        # Test status
        self.test_status_label = ttk.Label(test_frame, text="Click 'Start Test' to check face detection", style="Status.TLabel")
        self.test_status_label.pack(pady=10)

        # Test buttons
        button_row = ttk.Frame(test_frame)
        button_row.pack(pady=10)

        self.start_test_button = ttk.Button(button_row, text="Start Test", command=self.start_face_test)
        self.start_test_button.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_test_button = ttk.Button(button_row, text="Stop Test", command=self.stop_face_test, state="disabled")
        self.stop_test_button.pack(side=tk.LEFT)

        # Test results
        self.test_results_label = ttk.Label(test_frame, text="", style="Status.TLabel")
        self.test_results_label.pack(pady=10)

    def create_button_section(self, parent: ttk.Frame) -> None:
        """Create button section."""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        # Save button
        ttk.Button(
            button_frame,
            text="Save Settings",
            command=self.save_settings
        ).pack(side=tk.RIGHT, padx=(0, 10))

        # Back button
        if self.on_back:
            ttk.Button(
                button_frame,
                text="Back",
                command=self.on_back_clicked
            ).pack(side=tk.RIGHT)

    def populate_cameras(self) -> None:
        """Populate camera dropdown with available cameras."""
        try:
            # Get available cameras
            temp_detector = FaceDetector()
            available_cameras = temp_detector.get_available_cameras()
            temp_detector.cleanup()

            if available_cameras:
                camera_list = [f"Camera {i}" for i in available_cameras]
                self.camera_combo['values'] = camera_list
                self.camera_combo.current(0)
                self.camera_var.set(available_cameras[0])
                self.camera_status_label.config(text=f"Status: {len(available_cameras)} cameras found")
            else:
                self.camera_combo['values'] = ["No cameras found"]
                self.camera_combo.current(0)
                self.camera_status_label.config(text="Status: No cameras available")
                self.enable_var.set(False)

        except Exception as e:
            self.logger.error(f"Failed to populate cameras: {e}")
            self.camera_status_label.config(text="Status: Error checking cameras")

    def test_camera(self) -> None:
        """Test the selected camera."""
        try:
            camera_index = self.camera_var.get()

            # Create test detector
            self.test_detector = FaceDetector(camera_index=camera_index)

            if self.test_detector.test_camera():
                self.camera_status_label.config(text="Status: Camera working properly", foreground="#27ae60")
                messagebox.showinfo("Camera Test", "Camera is working properly!")
            else:
                self.camera_status_label.config(text="Status: Camera test failed", foreground="#e74c3c")
                messagebox.showerror("Camera Test", "Camera test failed. Please check camera connection.")

            # Cleanup
            if self.test_detector:
                self.test_detector.cleanup()
                self.test_detector = None

        except Exception as e:
            self.logger.error(f"Camera test error: {e}")
            self.camera_status_label.config(text="Status: Test error", foreground="#e74c3c")
            messagebox.showerror("Camera Test", f"Camera test failed: {e}")

    def start_face_test(self) -> None:
        """Start face detection test."""
        try:
            if self.test_detector and self.test_detector.is_monitoring:
                messagebox.showwarning("Test Already Running", "Face detection test is already running.")
                return

            # Create test detector with current settings
            camera_index = self.camera_var.get()
            detection_interval = self.interval_var.get()

            self.test_detector = FaceDetector(
                camera_index=camera_index,
                detection_interval=detection_interval,
                absence_threshold=self.threshold_var.get(),
                callback=self.on_test_event
            )

            if self.test_detector.start_monitoring():
                self.test_status_label.config(text="Face detection test running... Look at your camera!", foreground="#27ae60")
                self.start_test_button.config(state="disabled")
                self.stop_test_button.config(state="normal")
                self.test_results_label.config(text="")
                self.test_start_time = tk.time.time()
                self.test_detections = 0
                self.test_misses = 0
            else:
                messagebox.showerror("Test Failed", "Failed to start face detection test.")
                self.camera_status_label.config(text="Status: Test failed", foreground="#e74c3c")

        except Exception as e:
            self.logger.error(f"Start test error: {e}")
            messagebox.showerror("Test Error", f"Failed to start face detection test: {e}")

    def stop_face_test(self) -> None:
        """Stop face detection test."""
        try:
            if self.test_detector:
                self.test_detector.stop_monitoring()

                # Calculate test statistics
                total_time = tk.time.time() - self.test_start_time if hasattr(self, 'test_start_time') else 0
                stats = self.test_detector.get_monitoring_stats()

                # Display results
                self.test_status_label.config(text="Face detection test completed", foreground="#3498db")
                self.test_results_label.config(
                    text=f"Test Results:\n"
                    f"Duration: {total_time:.1f} seconds\n"
                    f"Face Detections: {stats['total_detections']}\n"
                    f"Misses: {stats['total_misses']}\n"
                    f"Detection Rate: {stats['detection_rate']:.1f}%"
                )

                # Cleanup
                self.test_detector.cleanup()
                self.test_detector = None

            self.start_test_button.config(state="normal")
            self.stop_test_button.config(state="disabled")

        except Exception as e:
            self.logger.error(f"Stop test error: {e}")
            messagebox.showerror("Test Error", f"Failed to stop face detection test: {e}")

    def on_test_event(self, event_type: str, is_present: bool) -> None:
        """Handle face detection test events."""
        if event_type == "face_detected":
            if is_present:
                self.test_detections += 1
            else:
                self.test_misses += 1

    def load_settings(self) -> None:
        """Load saved settings."""
        # In a real application, this would load from a config file
        # For now, use defaults
        pass

    def save_settings(self) -> None:
        """Save current settings."""
        try:
            self.settings = {
                'camera_index': self.camera_var.get(),
                'detection_interval': self.interval_var.get(),
                'absence_threshold': self.threshold_var.get(),
                'enable_monitoring': self.enable_var.get()
            }

            # Save to a simple config file
            import json
            with open('face_config.json', 'w') as f:
                json.dump(self.settings, f, indent=2)

            # Call save callback
            if self.on_save:
                self.on_save(self.settings)

            messagebox.showinfo("Settings Saved", "Face detection settings have been saved successfully.")
            self.logger.info("Face detection settings saved")

        except Exception as e:
            self.logger.error(f"Save settings error: {e}")
            messagebox.showerror("Save Error", f"Failed to save settings: {e}")

    def on_back_clicked(self) -> None:
        """Handle back button click."""
        if self.on_back:
            self.on_back()

    def get_frame(self) -> ttk.Frame:
        """Get the main frame widget."""
        return self.frame

    def show_frame(self) -> None:
        """Show the configuration frame."""
        self.frame.pack(fill=tk.BOTH, expand=True)

    def hide_frame(self) -> None:
        """Hide the configuration frame."""
        self.frame.pack_forget()

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.test_detector and self.test_detector.is_monitoring:
            self.test_detector.stop_monitoring()
            self.test_detector.cleanup()