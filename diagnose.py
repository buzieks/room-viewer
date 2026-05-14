#!/usr/bin/env python3
"""
Diagnostic and troubleshooting script for webcam viewer
"""

import sys
import os
import platform
import subprocess
import json
from pathlib import Path

class Diagnostic:
    """Run diagnostics on the system."""
    
    def __init__(self):
        self.results = {
            'system': {},
            'python': {},
            'project': {},
            'camera': {},
            'network': {},
            'issues': []
        }
    
    def run_all(self):
        """Run all diagnostics."""
        print("🔍 Running Diagnostics...\n")
        print("="*60)
        
        self.check_system()
        self.check_python()
        self.check_project()
        self.check_camera()
        self.check_network()
        
        self.print_results()
        self.print_recommendations()
    
    def check_system(self):
        """Check system information."""
        print("\n📋 System Information:")
        system = platform.system()
        release = platform.release()
        arch = platform.machine()
        
        self.results['system'] = {
            'os': system,
            'release': release,
            'architecture': arch
        }
        
        print(f"  OS: {system}")
        print(f"  Release: {release}")
        print(f"  Architecture: {arch}")
        
        if system == 'Linux':
            try:
                with open('/proc/cpuinfo', 'r') as f:
                    cpuinfo = f.read()
                    if 'BCM' in cpuinfo or 'ARMv' in cpuinfo:
                        print("  ✓ Raspberry Pi detected")
                        self.results['system']['pi'] = True
            except:
                pass
    
    def check_python(self):
        """Check Python environment."""
        print("\n🐍 Python Environment:")
        
        version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"  Python: {version}")
        self.results['python']['version'] = version
        
        if sys.version_info.major < 3 or sys.version_info.minor < 7:
            self.results['issues'].append("Python 3.7+ required")
            print("  ⚠️  Warning: Python 3.7+ is recommended")
        else:
            print("  ✓ Python version OK")
        
        # Check packages
        packages = ['flask', 'cv2', 'numpy']
        print("\n  Installed Packages:")
        
        for pkg in packages:
            try:
                if pkg == 'cv2':
                    import cv2
                    print(f"    ✓ OpenCV: {cv2.__version__}")
                else:
                    __import__(pkg)
                    print(f"    ✓ {pkg}")
            except ImportError:
                print(f"    ✗ {pkg} NOT INSTALLED")
                self.results['issues'].append(f"Missing package: {pkg}")
    
    def check_project(self):
        """Check project structure."""
        print("\n📁 Project Structure:")
        
        required_files = [
            'backend/app.py',
            'backend/camera.py',
            'backend/config.py',
            'backend/motion_detector.py',
            'backend/video_buffer.py',
            'backend/requirements.txt',
            'frontend/index.html',
            'frontend/styles.css',
            'frontend/script.js',
            'README.md'
        ]
        
        project_dir = os.path.dirname(os.path.abspath(__file__))
        
        for file_path in required_files:
            full_path = os.path.join(project_dir, file_path)
            exists = os.path.exists(full_path)
            status = "✓" if exists else "✗"
            print(f"  {status} {file_path}")
            
            if not exists:
                self.results['issues'].append(f"Missing file: {file_path}")
    
    def check_camera(self):
        """Check camera availability."""
        print("\n📷 Camera Check:")
        
        try:
            import cv2
            
            # Try to open camera
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    print("  ✓ Camera 0 accessible")
                    print(f"    Resolution: {frame.shape[1]}x{frame.shape[0]}")
                    self.results['camera']['available'] = True
                else:
                    print("  ⚠️  Camera 0 found but cannot capture frames")
                    self.results['camera']['available'] = False
                cap.release()
            else:
                print("  ✗ Camera 0 not accessible")
                print("    - Check if camera is connected")
                print("    - Try: ls -la /dev/video*")
                self.results['camera']['available'] = False
                self.results['issues'].append("Camera not accessible")
        
        except ImportError:
            print("  ⚠️  OpenCV not installed, cannot check camera")
    
    def check_network(self):
        """Check network information."""
        print("\n🌐 Network Information:")
        
        try:
            hostname = os.popen('hostname').read().strip()
            print(f"  Hostname: {hostname}")
            self.results['network']['hostname'] = hostname
        except:
            pass
        
        try:
            if platform.system() == 'Linux':
                ip_info = os.popen("hostname -I").read().strip()
            else:
                ip_info = os.popen("ipconfig").read()
            
            print(f"  IP Info: {ip_info[:100]}...")
            self.results['network']['ip'] = ip_info[:100]
        except:
            pass
        
        # Check port
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5000))
            sock.close()
            
            if result == 0:
                print("  ⚠️  Port 5000 is already in use")
                self.results['issues'].append("Port 5000 in use")
            else:
                print("  ✓ Port 5000 is available")
        except:
            print("  ? Could not check port availability")
    
    def print_results(self):
        """Print diagnostic results."""
        print("\n" + "="*60)
        print("📊 Diagnostic Summary")
        print("="*60)
        
        print(f"\nSystem: {self.results['system'].get('os', 'Unknown')}")
        print(f"Python: {self.results['python'].get('version', 'Unknown')}")
        print(f"Camera: {'Available' if self.results['camera'].get('available') else 'Not Available'}")
        
        if self.results['issues']:
            print(f"\n⚠️  Issues Found ({len(self.results['issues'])})")
            for i, issue in enumerate(self.results['issues'], 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✓ No issues detected!")
    
    def print_recommendations(self):
        """Print recommendations."""
        print("\n" + "="*60)
        print("💡 Recommendations")
        print("="*60)
        
        if not self.results['camera']['available']:
            print("\n📷 Camera Issues:")
            print("  1. Ensure camera is connected")
            print("  2. On Pi: Enable camera via raspi-config")
            print("  3. Test with: libcamera-hello -t 3")
            print("  4. Check: ls -la /dev/video*")
        
        if any('Missing package' in issue for issue in self.results['issues']):
            print("\n📦 Install Missing Packages:")
            print("  Run: pip install -r backend/requirements.txt")
        
        if 'Port 5000 in use' in self.results['issues']:
            print("\n🔌 Change Port:")
            print("  Edit backend/config.py and change PORT = 5001")
        
        print("\n🚀 To Start Application:")
        if platform.system() == 'Windows':
            print("  1. .\\venv\\Scripts\\activate")
            print("  2. cd backend")
            print("  3. python app.py")
        else:
            print("  1. source venv/bin/activate")
            print("  2. cd backend")
            print("  3. python3 app.py")
        
        print("\n🌐 Access at: http://localhost:5000")

if __name__ == '__main__':
    diag = Diagnostic()
    diag.run_all()
