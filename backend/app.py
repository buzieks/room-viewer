"""Main Flask application for webcam viewer."""

from flask import Flask, render_template, Response, jsonify, request
from flask_cors import CORS
import cv2
import threading
import time
from datetime import datetime
import os

from config import HOST, PORT, DEBUG, JPEG_QUALITY
from camera import CameraCapture
from motion_detector import MotionDetector
from video_buffer import VideoBuffer

app = Flask(__name__, template_folder='../frontend', static_folder='../frontend')
CORS(app)

# Global objects
camera = CameraCapture()
motion_detector = MotionDetector()
video_buffer = VideoBuffer()
show_motion_boxes = False


def generate_frames():
    """Generate frames for live stream."""
    while True:
        frame = camera.get_frame()

        if frame is None:
            time.sleep(0.01)
            continue

        # Detect motion
        motion_detected, contours = motion_detector.detect_motion(frame)

        # Add frame to buffer
        video_buffer.add_frame(frame, motion_detected, datetime.now())

        # Draw motion detection boxes if enabled
        if show_motion_boxes and contours:
            frame = motion_detector.draw_motion(frame, contours)

        # Add text overlay
        status_text = "MOTION DETECTED" if motion_detected else "No motion"
        color = (0, 0, 255) if motion_detected else (0, 255, 0)
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, color, 2)

        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n'
               b'Content-Length: ' + str(len(frame_bytes)).encode() + b'\r\n\r\n'
               + frame_bytes + b'\r\n')


@app.route('/')
def index():
    """Main page."""
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    """Video feed endpoint for live streaming."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/api/status')
def get_status():
    """Get current status including motion detection state."""
    frame = camera.get_frame()
    stats = video_buffer.get_buffer_stats()

    return jsonify({
        'camera_running': camera.is_running,
        'motion_detected': motion_detector.motion_detected,
        'show_motion_boxes': show_motion_boxes,
        'buffer_stats': stats,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/motion-events')
def get_motion_events():
    """Get list of motion events from buffer."""
    motion_events = video_buffer.get_motion_events()

    return jsonify({
        'count': len(motion_events),
        'events': [
            {
                'start_frame': event[0]['index'] if event else 0,
                'end_frame': event[-1]['index'] if event else 0,
                'duration_frames': len(event),
                'timestamp': event[0]['timestamp'].isoformat() if event else None
            }
            for event in motion_events
        ]
    })


@app.route('/api/rollback/<int:seconds_back>')
def get_rollback(seconds_back):
    """
    Get frames from specified seconds ago.

    Args:
        seconds_back: Number of seconds to roll back
    """
    if seconds_back < 1 or seconds_back > 60:
        seconds_back = 10

    rollback_frames = video_buffer.get_rollback_frames(seconds_back)

    # Return first and last frame as reference
    response = {
        'seconds_back': seconds_back,
        'total_frames': len(rollback_frames),
        'available': len(rollback_frames) > 0
    }

    if rollback_frames:
        response['start_time'] = rollback_frames[0]['timestamp'].isoformat()
        response['end_time'] = rollback_frames[-1]['timestamp'].isoformat()

    return jsonify(response)


@app.route('/api/toggle-motion-boxes', methods=['POST'])
def toggle_motion_boxes():
    """Toggle motion detection visualization."""
    global show_motion_boxes
    show_motion_boxes = not show_motion_boxes

    return jsonify({
        'show_motion_boxes': show_motion_boxes
    })


@app.route('/api/clear-buffer', methods=['POST'])
def clear_buffer():
    """Clear video buffer."""
    video_buffer.clear()
    motion_detector.reset()

    return jsonify({
        'status': 'Buffer cleared',
        'stats': video_buffer.get_buffer_stats()
    })


def startup():
    """Initialize camera on startup."""
    print("Starting webcam viewer...")
    if not camera.start():
        print("Failed to start camera. Make sure a camera is connected.")
        return False

    print(f"Camera started successfully")
    print(f"Server running at http://{HOST}:{PORT}")
    return True


@app.before_request
def before_request():
    """Check camera status before each request."""
    if not camera.is_running:
        print("Camera is not running, attempting to restart...")
        if not camera.start():
            print("Failed to restart camera")


@app.teardown_appcontext
def shutdown(exception=None):
    """Cleanup on shutdown."""
    print("Shutting down...")
    camera.stop()


if __name__ == '__main__':
    if startup():
        try:
            app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
        except KeyboardInterrupt:
            print("\nShutdown requested")
            camera.stop()
        finally:
            camera.stop()
    else:
        print("Failed to start application")
