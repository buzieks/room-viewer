"""Camera capture module for video acquisition."""

import cv2
import threading
from collections import deque
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, CAMERA_INDEX


class CameraCapture:
    """Handles video capture from camera."""

    def __init__(self):
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.is_running = False

    def start(self):
        """Initialize camera and start capturing frames."""
        try:
            self.cap = cv2.VideoCapture(CAMERA_INDEX)
            if not self.cap.isOpened():
                raise RuntimeError("Failed to open camera")

            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, VIDEO_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, VIDEO_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, VIDEO_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize buffer for low latency

            self.is_running = True
            # Start capture thread
            capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            capture_thread.start()
            return True
        except Exception as e:
            print(f"Error starting camera: {e}")
            return False

    def _capture_loop(self):
        """Continuous frame capture loop."""
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
            else:
                print("Failed to read frame")

    def get_frame(self):
        """Get the latest captured frame."""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """Stop camera capture."""
        self.is_running = False
        if self.cap:
            self.cap.release()

    def __del__(self):
        self.stop()
