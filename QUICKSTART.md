# 🚀 Quick Start Guide

## Windows (Development)

### Step 1: Install Python
1. Download Python 3.9+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Verify: Open PowerShell and run `python --version`

### Step 2: Setup Project
```powershell
# Navigate to project directory
cd "C:\Users\[YourUsername]\OneDrive\Documents\Projects\room-viewer"

# Run installation script
python install.py
```

### Step 3: Start the Application
```powershell
# Activate virtual environment
.\venv\Scripts\activate

# Start the app
cd backend
python app.py
```

### Step 4: Access the Viewer
Open your browser and go to: **http://localhost:5000**

---

## Raspberry Pi 5 (Production)

### Step 1: Prepare Your Raspberry Pi
```bash
# Connect to your Pi via SSH
ssh pi@raspberrypi.local

# Or if that doesn't work, find the IP
ping raspberrypi.local
ssh pi@<ip-address>
```

### Step 2: Clone the Project
```bash
cd ~
git clone <your-repo-url> room-viewer
cd room-viewer
```

### Step 3: Run Setup
```bash
chmod +x setup_raspberry_pi.sh
./setup_raspberry_pi.sh
```

### Step 4: Activate Environment & Install Dependencies
```bash
source venv/bin/activate
pip install -r backend/requirements.txt
```

### Step 5: Start the Application
```bash
# Option A: Direct start
chmod +x run.sh
./run.sh

# Option B: As a service (recommended)
sudo cp webcam-viewer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable webcam-viewer.service
sudo systemctl start webcam-viewer.service
```

### Step 6: Access from Anywhere
Find your Pi's IP address:
```bash
hostname -I
```

Then access: **http://<your-pi-ip>:5000**

---

## Camera Setup

### USB Webcam (Plug & Play)
1. Connect USB webcam to Raspberry Pi
2. The application will automatically detect it
3. Access the web interface and you should see live video

### Raspberry Pi Camera Module
```bash
# Enable camera
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Reboot
sudo reboot

# Test camera
libcamera-hello -t 3
```

---

## Common Issues & Quick Fixes

### "Camera not found"
```bash
# Check connected cameras
ls -la /dev/video*

# If nothing shows up, try USB camera driver
sudo apt-get install -y v4l-utils
v4l2-ctl --list-devices
```

### "Permission denied" on script
```bash
chmod +x run.sh
chmod +x setup_raspberry_pi.sh
```

### "Port 5000 already in use"
In `backend/config.py`, change:
```python
PORT = 5001  # Use a different port
```

### "High CPU usage"
In `backend/config.py`, reduce:
```python
VIDEO_FPS = 15  # Lower from 30
VIDEO_WIDTH = 480  # Lower from 640
VIDEO_HEIGHT = 360  # Lower from 480
JPEG_QUALITY = 70  # Lower from 85
```

---

## What You Get

✅ **Live 24/7 Monitoring**
- Real-time video streaming
- Motion detection with visual indicators
- Live statistics dashboard

✅ **Smart Rollback**
- Access footage from up to 10 seconds ago
- Automatically buffers motion events
- Perfect for security footage review

✅ **Lightweight**
- ~200MB RAM usage
- ~15-25% CPU on Raspberry Pi 5
- Works on WiFi or Ethernet

✅ **Easy Access**
- Web-based (no apps needed)
- Works on any device with a browser
- Mobile responsive design

---

## Next Steps

1. **Customize Motion Sensitivity**
   - Edit `backend/config.py`
   - Adjust `MOTION_THRESHOLD` (0-255)
   - Lower = more sensitive

2. **Set Auto-Start on Boot**
   - Use systemd service (recommended)
   - See README.md for detailed instructions

3. **Access Remotely**
   - Use SSH tunneling
   - Or use ngrok for internet access (advanced)

4. **Monitor Performance**
   - Check system stats in the UI
   - Adjust settings if needed

---

## Support & Resources

📖 **Full Documentation**: See `README.md` for comprehensive guide
🐛 **Issues**: Check Troubleshooting section in README.md
💡 **Configuration**: Edit `backend/config.py` for all settings
📊 **Performance**: Monitor via the web interface

**Enjoy your Webcam Viewer! 🎬**
