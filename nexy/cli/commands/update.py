"""
Author: Espoir Loém

This module provides functionality for updating Nexy to the latest version via the command line interface.
"""

import sys
import subprocess

def update():
    """
    Updates Nexy to the latest version using pip.
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "nexy"])
        print("✨ Nexy has been updated successfully!")
    except subprocess.CalledProcessError as e:
        print("❌ Error updating Nexy:", e)
        sys.exit(1)
