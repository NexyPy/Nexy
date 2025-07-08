import sys
import subprocess

def upgrade():
    """
    Upgrades Nexy to the latest version using pip
    """
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nexy","--force"])
        print("✨ Nexy has been upgraded successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error upgrading Nexy: {e}")
        sys.exit(1)



