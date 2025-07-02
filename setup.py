#!/usr/bin/env python3
"""
Setup script for Emergency Response System
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("🚨 Emergency Response System Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Install core dependencies first
    core_deps = [
        "vaderSentiment==3.3.2",
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "gradio==4.7.1",
        "sqlalchemy==2.0.23",
        "pydantic==2.5.0",
        "requests==2.31.0",
        "python-dotenv==1.0.0"
    ]
    
    print("\n📦 Installing core dependencies...")
    for dep in core_deps:
        if not run_command(f"pip install {dep}", f"Installing {dep}"):
            print(f"❌ Failed to install {dep}")
            return False
    
    print("\n🧪 Testing imports...")
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        print("✅ VaderSentiment import successful")
        
        import fastapi
        print("✅ FastAPI import successful")
        
        import gradio
        print("✅ Gradio import successful")
        
        import sqlalchemy
        print("✅ SQLAlchemy import successful")
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False
    
    print("\n🎉 Setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nNext steps:")
        print("1. Run: python test_system.py")
        print("2. Start backend: python backend/main.py")
        print("3. Start frontend: python frontend/main_gradio.py")
    else:
        print("\nSetup failed. Please check the errors above.")
        sys.exit(1)
