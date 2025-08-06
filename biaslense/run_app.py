#!/usr/bin/env python3
"""
BiasLens - Run Script
Simple script to launch the BiasLens Streamlit application
"""

import subprocess
import sys
import os

def main():
    """Run the BAMIP Streamlit app"""
    print("🧠 Starting BAMIP Pipeline...")
    print("📱 Opening BAMIP Streamlit application...")
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, "app", "bamip_multipage.py")
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 BiasLens stopped by user")
    except Exception as e:
        print(f"❌ Error running BiasLens: {e}")
        print("Make sure you have installed the requirements:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    main() 