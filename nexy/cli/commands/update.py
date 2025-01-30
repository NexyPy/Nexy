import os
import sys
import subprocess
from pathlib import Path

def update():
    """
    Updates Nexy to the latest version using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "nexy"])
        print("✨ Nexy has been updated successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Error updating Nexy:", e)
        sys.exit(1)
