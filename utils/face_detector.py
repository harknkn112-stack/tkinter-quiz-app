"""
Face Detection Module for Quiz Application
Monitors user attention and detects when user looks away from screen.
"""

import cv2
import numpy as np
import threading
import time
from typing import Optional, Callable, Tuple
from datetime import datetime
import os
import logging


class FaceDetector:
    """
    Face detection and attention monitoring system.
    Detects user's face and monitors for attention/absence.
    """

    def __init__(self,
                 camera_index: int = 0,
                 detection_interval: float = 1.0,
                 absence_threshold: int = 3,
                 callback: Optional[Callable[[str, bool], None]] = None):
        """
        Initialize face detector.

        Args:
            camera_index: Camera device index (default: 0)
            detection_interval: Seconds between face detection checks
            absence_threshold: Number of consecutive misses before marking as away
            callback: Function to call with detection results
        """
        self.camera_index = camera_index
        self.detection_interval = detection_interval
        self.absence_threshold = absence_threshold
        self.callback = callback

        # Detection state
        self.is_running = False
        self.is_monitoring = False
        self.detection_thread = None
        self.camera = None

        # Face detection state
        self.consecutive_misses = 0
        self.last_detection_time = None
        self.total_detections = 0
        self.total_misses = 0

        # Face detection classifier
        self.face_cascade = None
        self.load_face_classifier()

        # Logging
        self.logger = logging.getLogger('quiz_app')

    def load_face_classifier(self) -> None:
        """Load the face detection classifier."""
        try:
            # Try to load OpenCV's built-in face cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            if os.path.exists(cascade_path):
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                self.logger.info("Face detection classifier loaded successfully")
            else:
                self.logger.warning(f"Face cascade file not found at: {cascade_path}")
                self.face_cascade = None
        except Exception as e:
            self.logger.error(f"Failed to load face classifier: {e}")
            self.face_cascade = None

    def initialize_camera(self) -> bool:
        """
        Initialize the camera for face detection.

        Returns:
            True if camera initialized successfully
        """
        try:
            self.camera = cv2.VideoCapture(self.camera_index)

            # Check if camera opened successfully
            if not self.camera.isOpened():
                self.logger.error(f"Failed to open camera at index {self.camera_index}")
                return False

            # Set camera properties
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            self.camera.set(cv2.CAP_PROP_FPS, 30)

            # Test camera by reading a frame
            ret, frame = self.camera.read()
            if not ret or frame is None:
                self.logger.error("Failed to read from camera")
                return False

            self.logger.info(f"Camera initialized successfully at index {self.camera_index}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to initialize camera: {e}")
            return False

    def detect_faces(self, frame: np.ndarray) -> Tuple[bool, list]:
        """
        Detect faces in the given frame.

        Args:
            frame: Image frame to process

        Returns:
            Tuple of (faces_detected, face_coordinates)
        """
        if self.face_cascade is None:
            return False, []

        try:
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            faces_detected = len(faces) > 0
            return faces_detected, faces.tolist()

        except Exception as e:
            self.logger.error(f"Error during face detection: {e}")
            return False, []

    def calculate_attention_score(self, frame: np.ndarray, face_coords: list) -> float:
        """
        Calculate attention score based on face position and size.

        Args:
            frame: Image frame
            face_coords: List of face coordinates

        Returns:
            Attention score between 0.0 and 1.0
        """
        if not face_coords:
            return 0.0

        try:
            frame_height, frame_width = frame.shape[:2]
            max_score = 0.0

            for (x, y, w, h) in face_coords:
                # Calculate face center
                face_center_x = x + w // 2
                face_center_y = y + h // 2

                # Calculate distance from frame center
                frame_center_x = frame_width // 2
                frame_center_y = frame_height // 2

                distance = np.sqrt((face_center_x - frame_center_x)**2 +
                                 (face_center_y - frame_center_y)**2)

                # Maximum possible distance (corner to corner)
                max_distance = np.sqrt((frame_width//2)**2 + (frame_height//2)**2)

                # Normalize distance (closer to center = higher score)
                position_score = 1.0 - (distance / max_distance)

                # Size score (larger face = more attentive, assuming consistent distance)
                face_area = w * h
                frame_area = frame_width * frame_height
                size_score = min(face_area / frame_area * 10, 1.0)  # Normalize to 0-1

                # Combined score for this face
                face_score = (position_score * 0.6) + (size_score * 0.4)
                max_score = max(max_score, face_score)

            return max_score

        except Exception as e:
            self.logger.error(f"Error calculating attention score: {e}")
            return 0.0

    def monitor_attention(self) -> None:
        """Main monitoring loop that runs in a separate thread."""
        while self.is_monitoring:
            try:
                if not self.camera or not self.camera.isOpened():
                    time.sleep(self.detection_interval)
                    continue

                ret, frame = self.camera.read()
                if not ret or frame is None:
                    time.sleep(self.detection_interval)
                    continue

                # Detect faces
                faces_detected, face_coords = self.detect_faces(frame)

                # Calculate attention score
                attention_score = self.calculate_attention_score(frame, face_coords) if faces_detected else 0.0

                # Update statistics
                current_time = datetime.now()

                if faces_detected:
                    self.consecutive_misses = 0
                    self.last_detection_time = current_time
                    self.total_detections += 1

                    # Check if user is looking away (low attention score)
                    is_looking_away = attention_score < 0.3  # Threshold for "looking away"

                    if self.callback:
                        self.callback("face_detected", not is_looking_away)

                    self.logger.debug(f"Face detected - Attention score: {attention_score:.2f}")
                else:
                    self.consecutive_misses += 1
                    self.total_misses += 1

                    if self.consecutive_misses >= self.absence_threshold:
                        if self.callback:
                            self.callback("user_away", True)
                        self.logger.info(f"User looking away - {self.consecutive_misses} consecutive misses")
                    else:
                        self.logger.debug(f"No face detected - Misses: {self.consecutive_misses}")

                time.sleep(self.detection_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.detection_interval)

    def start_monitoring(self) -> bool:
        """
        Start face monitoring.

        Returns:
            True if monitoring started successfully
        """
        try:
            if self.is_monitoring:
                self.logger.warning("Face monitoring is already running")
                return True

            if not self.initialize_camera():
                self.logger.error("Failed to initialize camera for monitoring")
                return False

            self.is_monitoring = True

            # Start monitoring thread
            self.detection_thread = threading.Thread(target=self.monitor_attention, daemon=True)
            self.detection_thread.start()

            self.logger.info("Face monitoring started")
            return True

        except Exception as e:
            self.logger.error(f"Failed to start face monitoring: {e}")
            return False

    def stop_monitoring(self) -> None:
        """Stop face monitoring."""
        try:
            self.is_monitoring = False

            # Wait for thread to finish
            if self.detection_thread and self.detection_thread.is_alive():
                self.detection_thread.join(timeout=2.0)

            # Release camera
            if self.camera:
                self.camera.release()
                self.camera = None

            self.logger.info("Face monitoring stopped")

        except Exception as e:
            self.logger.error(f"Error stopping face monitoring: {e}")

    def get_monitoring_stats(self) -> dict:
        """
        Get current monitoring statistics.

        Returns:
            Dictionary with monitoring statistics
        """
        total_checks = self.total_detections + self.total_misses
        detection_rate = (self.total_detections / total_checks * 100) if total_checks > 0 else 0

        return {
            'is_monitoring': self.is_monitoring,
            'total_detections': self.total_detections,
            'total_misses': self.total_misses,
            'detection_rate': round(detection_rate, 2),
            'consecutive_misses': self.consecutive_misses,
            'last_detection': self.last_detection_time.isoformat() if self.last_detection_time else None
        }

    def test_camera(self) -> bool:
        """
        Test if camera is working.

        Returns:
            True if camera is functional
        """
        try:
            temp_camera = cv2.VideoCapture(self.camera_index)
            ret, frame = temp_camera.read()
            temp_camera.release()

            if ret and frame is not None:
                self.logger.info("Camera test successful")
                return True
            else:
                self.logger.error("Camera test failed - no frame captured")
                return False

        except Exception as e:
            self.logger.error(f"Camera test error: {e}")
            return False

    def get_available_cameras(self) -> list:
        """
        Get list of available camera devices.

        Returns:
            List of available camera indices
        """
        available_cameras = []

        for i in range(5):  # Check first 5 camera indices
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    available_cameras.append(i)
                cap.release()

        return available_cameras

    def cleanup(self) -> None:
        """Clean up resources."""
        self.stop_monitoring()

        if self.camera:
            self.camera.release()
            self.camera = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.cleanup()