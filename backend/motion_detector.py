"""Motion detection module using OpenCV."""

import cv2
import numpy as np
from config import (
    MOTION_THRESHOLD,
    MIN_CONTOUR_AREA,
    MOTION_BLUR_SIZE,
)


class MotionDetector:
    """Detects motion in video frames."""

    def __init__(self):
        self.previous_frame = None
        self.motion_detected = False
        self.motion_contours = []

    def detect_motion(self, frame):
        """
        Detect motion in the given frame.

        Args:
            frame: Input frame from camera

        Returns:
            tuple: (motion_detected: bool, contours: list of motion areas)
        """
        if frame is None:
            return False, []

        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        gray = cv2.GaussianBlur(gray, MOTION_BLUR_SIZE, 0)

        # Initialize previous frame
        if self.previous_frame is None:
            self.previous_frame = gray
            return False, []

        # Calculate frame difference
        frame_delta = cv2.absdiff(self.previous_frame, gray)
        thresh = cv2.threshold(frame_delta, MOTION_THRESHOLD, 255, cv2.THRESH_BINARY)[1]

        # Dilate threshold to fill holes
        thresh = cv2.dilate(thresh, None, iterations=2)

        # Find contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours by minimum area
        significant_contours = []
        motion_detected = False

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > MIN_CONTOUR_AREA:
                significant_contours.append(contour)
                motion_detected = True

        self.previous_frame = gray
        self.motion_detected = motion_detected
        self.motion_contours = significant_contours

        return motion_detected, significant_contours

    def draw_motion(self, frame, contours):
        """
        Draw motion detection rectangles on frame.

        Args:
            frame: Input frame
            contours: List of motion contours

        Returns:
            Annotated frame with rectangles
        """
        frame_copy = frame.copy()

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)

        return frame_copy

    def reset(self):
        """Reset motion detector state."""
        self.previous_frame = None
        self.motion_detected = False
        self.motion_contours = []
