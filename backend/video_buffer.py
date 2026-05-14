"""Video buffering module for storing frames and enabling rollback."""

import cv2
from collections import deque
from config import BUFFER_SIZE, MOTION_MEMORY_FRAMES
import threading


class VideoBuffer:
    """Circular buffer for storing video frames and motion history."""

    def __init__(self, buffer_size=BUFFER_SIZE):
        self.buffer_size = buffer_size
        self.frame_buffer = deque(maxlen=buffer_size)
        self.timestamp_buffer = deque(maxlen=buffer_size)
        self.motion_buffer = deque(maxlen=buffer_size)
        self.motion_memory = deque(maxlen=MOTION_MEMORY_FRAMES)
        self.lock = threading.Lock()
        self.frame_count = 0

    def add_frame(self, frame, motion_detected=False, timestamp=None):
        """
        Add a frame to the buffer.

        Args:
            frame: Frame to add
            motion_detected: Whether motion was detected in this frame
            timestamp: Timestamp of the frame
        """
        with self.lock:
            # Store frame
            self.frame_buffer.append(frame.copy())
            self.timestamp_buffer.append(timestamp)
            self.motion_buffer.append(motion_detected)

            # Maintain motion memory
            if motion_detected:
                self.motion_memory.append(self.frame_count)

            self.frame_count += 1

    def get_latest_frame(self):
        """Get the latest frame from buffer."""
        with self.lock:
            if self.frame_buffer:
                return self.frame_buffer[-1].copy()
            return None

    def get_motion_events(self):
        """
        Get frames around motion events.

        Returns:
            List of frame sequences (before, during, after motion)
        """
        with self.lock:
            if not self.motion_buffer:
                return []

            motion_events = []
            motion_indices = [i for i, m in enumerate(self.motion_buffer) if m]

            if not motion_indices:
                return []

            # Group consecutive motion frames
            event_groups = []
            current_group = [motion_indices[0]]

            for idx in motion_indices[1:]:
                if idx - current_group[-1] <= 5:  # Allow up to 5 frames gap
                    current_group.append(idx)
                else:
                    event_groups.append(current_group)
                    current_group = [idx]

            event_groups.append(current_group)

            # Extract frame sequences around motion
            for group in event_groups:
                start_idx = max(0, group[0] - MOTION_MEMORY_FRAMES // 2)
                end_idx = min(len(self.frame_buffer) - 1, group[-1] + MOTION_MEMORY_FRAMES // 4)

                event_frames = []
                for i in range(start_idx, end_idx + 1):
                    if i < len(self.frame_buffer):
                        event_frames.append({
                            'frame': self.frame_buffer[i],
                            'index': i,
                            'timestamp': self.timestamp_buffer[i],
                            'motion': self.motion_buffer[i]
                        })

                if event_frames:
                    motion_events.append(event_frames)

            return motion_events

    def get_rollback_frames(self, seconds_back=10, fps=30):
        """
        Get frames from the specified number of seconds ago.

        Args:
            seconds_back: How many seconds to roll back
            fps: Frames per second

        Returns:
            List of frames from the rollback period
        """
        with self.lock:
            frames_to_get = min(seconds_back * fps, len(self.frame_buffer))
            rollback_frames = []

            for i in range(max(0, len(self.frame_buffer) - frames_to_get), len(self.frame_buffer)):
                rollback_frames.append({
                    'frame': self.frame_buffer[i],
                    'index': i,
                    'timestamp': self.timestamp_buffer[i],
                    'motion': self.motion_buffer[i]
                })

            return rollback_frames

    def get_buffer_stats(self):
        """Get buffer statistics."""
        with self.lock:
            motion_count = sum(1 for m in self.motion_buffer if m)
            return {
                'total_frames': self.frame_count,
                'buffered_frames': len(self.frame_buffer),
                'motion_events': motion_count,
                'buffer_size': self.buffer_size
            }

    def clear(self):
        """Clear all buffers."""
        with self.lock:
            self.frame_buffer.clear()
            self.timestamp_buffer.clear()
            self.motion_buffer.clear()
            self.motion_memory.clear()
            self.frame_count = 0
