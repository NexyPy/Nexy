import os
import sys
import subprocess
from pathlib import Path

def upgrade():
    """
    Upgrades Nexy to the latest version using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "nexy"])
        print("✨ Nexy has been upgraded successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Error upgrading Nexy:", e)
        sys.exit(1)
