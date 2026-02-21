from typing import Optional
import subprocess

def uvicorn(port: Optional[int] = None):
    try:
        subprocess.call(["uvicorn", "nexy.server.app:_server", "--reload"])
    except Exception as e:
        print(e)

def granian (port: Optional[int] = None):
    try:
        subprocess.call(["granian", "nexy.server.app:_server", "--reload"])
    except Exception as e:
        print(e)

def vite(port: Optional[int] = None):
    try:
        subprocess.call(["npm", "run", "dev", "--port", str(port)])
    except Exception as e:
        print(e)