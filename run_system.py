#!/usr/bin/env python3
"""
Quick launcher for Emergency Response System
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def run_backend():
    """Run the FastAPI backend"""
    print("🚀 Starting FastAPI Backend...")
    subprocess.run([sys.executable, "backend/main.py"], cwd=Path(__file__).parent)

def run_frontend():
    """Run the Gradio frontend"""
    print("🎨 Starting Gradio Frontend...")
    time.sleep(3)  # Wait for backend to start
    subprocess.run([sys.executable, "frontend/main_gradio.py"], cwd=Path(__file__).parent)

def main():
    """Main launcher function"""
    print("🚨 Emergency Response System Launcher")
    print("=" * 50)
    
    print("Starting both backend and frontend...")
    print("🌐 Backend will be at: http://localhost:8000")
    print("🎭 Frontend will be at: http://localhost:7860")
    print("\nPress Ctrl+C to stop both services")
    print("=" * 50)
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Emergency Response System...")
        print("Thank you for using the system!")

if __name__ == "__main__":
    main()
