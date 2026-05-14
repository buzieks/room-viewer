"""Configuration settings for the webcam viewer application."""

import os

# Video settings
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 30
CAMERA_INDEX = 0  # 0 for default camera, change if multiple cameras

# Motion detection settings
MOTION_THRESHOLD = 30  # Threshold for motion detection (0-255)
MIN_CONTOUR_AREA = 500  # Minimum contour area to be considered as motion
MOTION_BLUR_SIZE = (21, 21)  # Gaussian blur size for motion detection

# Buffering settings (for rollback capability)
BUFFER_SIZE = 300  # Store last 300 frames (~10 seconds at 30fps)
MOTION_MEMORY_FRAMES = 150  # Store 150 frames before motion detected (~5 seconds)

# Server settings
HOST = '0.0.0.0'
PORT = 5000
DEBUG = False

# JPEG quality for streaming
JPEG_QUALITY = 85

# Directories
BASEDIR = os.path.abspath(os.path.dirname(__file__))
RECORDINGS_DIR = os.path.join(os.path.dirname(BASEDIR), 'recordings')

# Ensure recordings directory exists
if not os.path.exists(RECORDINGS_DIR):
    os.makedirs(RECORDINGS_DIR)
