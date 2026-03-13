#!/usr/bin/env python3
"""
Security Intelligence & Suspect Tracking System
Startup Script
"""

import os
import sys
import subprocess
import argparse

def check_dependencies():
    """Check if required dependencies are installed"""
    print("[*] Checking dependencies...")
    
    required_packages = [
        'flask',
        'face_recognition',
        'cv2',
        'PIL',
        'numpy',
        'requests',
        'bs4'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"[!] Missing packages: {', '.join(missing)}")
        print("[*] Installing missing dependencies...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("[✓] Dependencies installed successfully")
    else:
        print("[✓] All dependencies are installed")

def setup_directories():
    """Create necessary directories"""
    print("[*] Setting up directories...")
    
    directories = [
        'static/uploads',
        'static/faces',
        'static/results'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("[✓] Directories created")

def initialize_database():
    """Initialize the database"""
    print("[*] Initializing database...")
    
    from app import init_database
    init_database()
    
    print("[✓] Database initialized")

def start_server(host='0.0.0.0', port=5000, debug=False):
    """Start the Flask server"""
    print(f"[*] Starting server on {host}:{port}...")
    
    from app import app
    app.run(host=host, port=port, debug=debug)

def main():
    parser = argparse.ArgumentParser(description='Security Intelligence & Suspect Tracking System')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--setup', action='store_true', help='Run setup only')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("  SECURITY INTELLIGENCE & SUSPECT TRACKING SYSTEM")
    print("=" * 70)
    print()
    
    # Setup
    check_dependencies()
    setup_directories()
    initialize_database()
    
    if args.setup:
        print("\n[✓] Setup completed successfully")
        return
    
    # Start server
    print()
    print("=" * 70)
    print(f"  Server starting at http://{args.host}:{args.port}")
    print("=" * 70)
    print()
    
    start_server(args.host, args.port, args.debug)

if __name__ == '__main__':
    main()
