import os
import sys
import subprocess
from pathlib import Path

def install():
    """
    Installs Nexy dependencies using pip
    """
    try:
        # Check if requirements.txt exists
        if os.path.exists('requirements.txt'):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✨ Dependencies installed successfully!")
        else:
            print("❌ No requirements.txt file found")
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("❌ Error installing dependencies:", e)
        sys.exit(1)