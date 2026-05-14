#!/usr/bin/env python3
"""
Quick installation and configuration script for webcam viewer
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, description=""):
    """Run a shell command and return success status."""
    print(f"\n{'='*50}")
    if description:
        print(f"📦 {description}")
    print(f"Running: {' '.join(cmd)}")
    print('='*50)
    
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        return False
    except FileNotFoundError as e:
        print(f"❌ Command not found: {e}")
        return False

def main():
    """Main installation routine."""
    print("\n" + "="*50)
    print("🎬 Webcam Viewer - Installation Script")
    print("="*50)
    
    # Detect OS
    system = platform.system()
    print(f"\nDetected OS: {system}")
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print("❌ Python 3.7+ is required")
        sys.exit(1)
    
    # Get project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print(f"\nProject directory: {script_dir}")
    
    # Check if venv exists
    venv_dir = os.path.join(script_dir, 'venv')
    
    if not os.path.exists(venv_dir):
        print("\n📝 Creating virtual environment...")
        if not run_command([sys.executable, '-m', 'venv', 'venv'],
                          "Creating Python virtual environment"):
            print("❌ Failed to create virtual environment")
            sys.exit(1)
    else:
        print("✓ Virtual environment already exists")
    
    # Get pip path
    if system == 'Windows':
        pip_path = os.path.join(venv_dir, 'Scripts', 'pip.exe')
        python_path = os.path.join(venv_dir, 'Scripts', 'python.exe')
    else:
        pip_path = os.path.join(venv_dir, 'bin', 'pip')
        python_path = os.path.join(venv_dir, 'bin', 'python')
    
    # Install dependencies
    print("\n📦 Installing Python packages...")
    if not run_command([pip_path, 'install', '-r', 'backend/requirements.txt'],
                      "Installing required packages"):
        print("❌ Failed to install packages")
        sys.exit(1)
    
    # Success
    print("\n" + "="*50)
    print("✅ Installation Complete!")
    print("="*50)
    
    if system == 'Windows':
        print(f"\n📌 To start the application:")
        print(f"1. Open Command Prompt or PowerShell")
        print(f"2. Navigate to: {script_dir}")
        print(f"3. Run: .\\venv\\Scripts\\activate")
        print(f"4. Run: cd backend && python app.py")
        print(f"\n🌐 Access the viewer at: http://localhost:5000")
    else:
        print(f"\n📌 To start the application:")
        print(f"1. Run: source venv/bin/activate")
        print(f"2. Run: cd backend && python3 app.py")
        print(f"\n🌐 Access the viewer at: http://localhost:5000")
    
    print("\n" + "="*50)

if __name__ == '__main__':
    main()
