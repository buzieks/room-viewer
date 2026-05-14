# 📹 Live Webcam Viewer with Motion Detection & Rollback

A lightweight, real-time webcam viewer with motion detection and frame rollback capability designed to run on Raspberry Pi 5.

## Features

✨ **Live Video Streaming** - Real-time MJPEG stream from USB or Pi camera
🎯 **Motion Detection** - Automatic motion detection with visual overlays
⏮️ **Frame Rollback** - Access frames from up to 10 seconds ago
📊 **Real-time Status** - Live monitoring of motion events and buffer statistics
🌐 **Web-based UI** - No installation required, just a modern web browser
🍓 **Raspberry Pi 5 Optimized** - Lightweight and efficient resource usage
🔧 **Easy Setup** - Simple installation script and systemd service support

## System Requirements

- **Hardware**: Raspberry Pi 5 (or any Linux system with Python 3.7+)
- **Camera**: USB Webcam or Raspberry Pi Camera Module (CSI/DSI)
- **Storage**: 2GB+ available space
- **RAM**: 2GB+ available (Raspberry Pi 5 has 4GB+)
- **Network**: Ethernet or WiFi for web access

## Installation

### 1. Clone/Download the Project

```bash
cd ~
git clone <repository-url> room-viewer
cd room-viewer
```

### 2. Run Setup Script

```bash
chmod +x setup_raspberry_pi.sh
./setup_raspberry_pi.sh
```

This script will:
- Update system packages
- Install Python 3 and pip
- Install OpenCV dependencies
- Create a Python virtual environment
- Download all required packages

### 3. Install Python Dependencies

```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

## Quick Start

### Option 1: Direct Execution

```bash
# Make the run script executable
chmod +x run.sh

# Start the application
./run.sh

# The viewer will be available at:
# http://<raspberry-pi-ip>:5000
```

### Option 2: Using systemd Service (Auto-start on Boot)

```bash
# Copy service file to systemd directory
sudo cp webcam-viewer.service /etc/systemd/system/

# Edit the service file to match your setup
sudo nano /etc/systemd/system/webcam-viewer.service
# Update WorkingDirectory and ExecStart paths if needed

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable webcam-viewer.service
sudo systemctl start webcam-viewer.service

# Check status
sudo systemctl status webcam-viewer.service

# View logs
sudo journalctl -u webcam-viewer.service -f
```

### Option 3: Run in Background

```bash
source venv/bin/activate
cd backend
nohup python3 app.py > ../logs/webcam-viewer.log 2>&1 &
```

## Configuration

Edit `backend/config.py` to customize:

### Video Settings
```python
VIDEO_WIDTH = 640           # Frame width
VIDEO_HEIGHT = 480          # Frame height
VIDEO_FPS = 30              # Frames per second
CAMERA_INDEX = 0            # Camera device index
```

### Motion Detection
```python
MOTION_THRESHOLD = 30       # Sensitivity (0-255)
MIN_CONTOUR_AREA = 500      # Minimum motion size
MOTION_BLUR_SIZE = (21, 21) # Blur kernel size
```

### Buffer & Rollback
```python
BUFFER_SIZE = 300           # Total frames to buffer (~10s at 30fps)
MOTION_MEMORY_FRAMES = 150  # Frames before motion (~5s)
```

### Server
```python
HOST = '0.0.0.0'            # Bind address
PORT = 5000                 # Port number
JPEG_QUALITY = 85           # Stream quality (0-100)
```

## Usage

### Web Interface

1. **Open Browser**: Navigate to `http://<pi-ip>:5000`

2. **Live View**: Real-time video stream with motion detection indicator

3. **Motion Detection**:
   - "Show Motion Detection" button toggles detection visualization
   - Green rectangles appear when motion is detected
   - Motion badge appears in top-right corner

4. **Rollback Control**:
   - Adjust slider to select seconds to roll back (1-10s)
   - Click "Get Rollback Frames" to view previous frames
   - Information shows available frames for the selected period

5. **Buffer Management**:
   - Real-time display of buffered frames
   - Motion event history
   - "Clear Buffer" button resets all stored frames

### REST API Endpoints

```bash
# Get live video feed
GET /video_feed

# Get current status
GET /api/status
# Response: {
#   "camera_running": true,
#   "motion_detected": false,
#   "buffer_stats": {...}
# }

# Get motion events
GET /api/motion-events
# Response: {
#   "count": 5,
#   "events": [...]
# }

# Get rollback frames
GET /api/rollback/<seconds>
# Example: GET /api/rollback/5
# Response: {
#   "total_frames": 150,
#   "available": true,
#   "start_time": "2024-01-15T12:30:45.123456",
#   "end_time": "2024-01-15T12:30:50.123456"
# }

# Toggle motion boxes
POST /api/toggle-motion-boxes
# Response: {"show_motion_boxes": true}

# Clear buffer
POST /api/clear-buffer
# Response: {"status": "Buffer cleared", "stats": {...}}
```

## Camera Setup

### USB Webcam

Most USB webcams work out of the box. If multiple cameras are connected:

```python
# In config.py
CAMERA_INDEX = 0  # Change to 1, 2, etc. for different cameras

# To find available cameras
for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Camera {i} available")
        cap.release()
```

### Raspberry Pi Camera Module

For Raspberry Pi CSI Camera:

```bash
# Enable camera in raspi-config
sudo raspi-config
# Select Interfacing Options > Camera > Enable

# Verify camera is working
libcamera-hello -t 0

# The app will auto-detect the camera
```

## Performance Optimization for Raspberry Pi 5

1. **Video Resolution**: Reduce to 640x480 for better performance
2. **Frame Rate**: Set to 15-24 FPS for lighter load
3. **JPEG Quality**: Reduce to 70-80 for faster encoding
4. **Buffer Size**: Adjust based on available RAM

```python
# In config.py for optimized performance
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
VIDEO_FPS = 24
JPEG_QUALITY = 75
BUFFER_SIZE = 200
```

## Troubleshooting

### Camera Not Found
```bash
# Check connected cameras
ls /dev/video*

# Or in Python
python3 -c "import cv2; print('Cameras:', [cv2.VideoCapture(i).isOpened() for i in range(5)])"
```

### High CPU Usage
- Reduce VIDEO_FPS in config.py
- Reduce VIDEO_WIDTH and VIDEO_HEIGHT
- Reduce JPEG_QUALITY
- Disable motion visualization when not needed

### Connection Issues
```bash
# Check Pi's IP address
hostname -I

# Test local access
curl http://localhost:5000

# Check firewall
sudo ufw allow 5000/tcp
```

### Memory Issues
```bash
# Monitor memory usage
free -h

# Reduce buffer size in config.py
BUFFER_SIZE = 100  # Reduce from 300
```

### Service Won't Start
```bash
# Check service status
sudo systemctl status webcam-viewer.service

# View error logs
sudo journalctl -u webcam-viewer.service -n 50

# Verify paths in webcam-viewer.service are correct
sudo nano /etc/systemd/system/webcam-viewer.service
```

## Network Access

### Local Network
- Access from any device on the same network: `http://<pi-ip>:5000`

### Remote Access (Advanced)
```bash
# Using SSH tunneling
ssh -L 5000:localhost:5000 pi@<pi-ip>
# Then access: http://localhost:5000

# Using ngrok (expose to internet)
./ngrok http 5000
```

## Security Considerations

⚠️ **Important**: This application is designed for local/trusted networks.

For production use:
1. **Enable HTTPS**: Use nginx with SSL certificates
2. **Add Authentication**: Implement password protection
3. **Firewall**: Restrict access with ufw or iptables
4. **Network**: Run on isolated/private networks only

## Performance Metrics (Raspberry Pi 5)

Typical resource usage:
- **CPU**: 15-25% (depends on resolution and FPS)
- **RAM**: 200-300MB
- **Disk**: ~50MB (for application code and dependencies)
- **Network**: 2-5 Mbps (depends on quality settings)

## Development

### Project Structure
```
room-viewer/
├── backend/
│   ├── app.py              # Flask application
│   ├── camera.py           # Camera capture module
│   ├── motion_detector.py  # Motion detection logic
│   ├── video_buffer.py     # Frame buffering
│   ├── config.py           # Configuration
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── index.html          # Web interface
│   ├── styles.css          # Styling
│   └── script.js           # Client-side logic
├── run.sh                  # Startup script
├── setup_raspberry_pi.sh   # Setup script
├── webcam-viewer.service   # Systemd service
└── README.md               # This file
```

### Adding Features

To extend functionality:
1. Add new endpoints in `backend/app.py`
2. Update `backend/config.py` with new settings
3. Add UI elements in `frontend/index.html`
4. Handle interactions in `frontend/script.js`

### Debug Mode

```bash
# Enable debug logging
cd backend
DEBUG=True python3 app.py
```

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review logs in `journalctl` or `nohup.out`
3. Verify camera is working: `libcamera-hello` or `cheese`
4. Test network connectivity and firewall rules

## Future Enhancements

- 📹 Video recording and export
- 🎥 Multi-camera support
- 📊 Advanced analytics and heatmaps
- 🔐 Authentication and user management
- ☁️ Cloud backup integration
- 📱 Mobile app
- 🎬 Night vision/IR support
- ⚙️ Advanced motion filters

---

**Happy Streaming! 🎬**
