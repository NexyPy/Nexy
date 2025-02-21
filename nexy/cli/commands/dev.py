import logging
from  os import system, path, environ
import subprocess
from sys import platform
import typer
from rich.prompt import  IntPrompt


from nexy.cli.core.constants import Console,CMD
from nexy.cli.core.utils import get_next_available_port, print_banner

logging.basicConfig(level=logging.INFO)

def activate_virtualenv():
    """Activate the virtual environment if not already activated."""
    if 'VIRTUAL_ENV' not in environ:
        venv_path = "nexy_env/Scripts/activate" if platform == "win32" else "nexy_env/bin/activate"
        if path.exists(venv_path):
            logging.info("Activating virtual environment...")
            activate_command = f"source {venv_path}" if platform != "win32" else venv_path
            subprocess.run(activate_command, shell=True, check=True)
        else:
            logging.error("Virtual environment not found. Please create it first.")
            raise SystemExit(1)

@CMD.command()
def dev(
    port: int = typer.Option(3000, "--port", "-p", help="Port du serveur"),
    host: str = typer.Option("localhost", "--host", help="Host du serveur"),
    worker: int = typer.Option(1, help="Nombre de workers")
) -> None:
    """Lance le serveur"""
    try:
        activate_virtualenv()
        port = get_next_available_port(port)
        print_banner()
        Console.print(f"[green]Server started on [yellow]http://{host}:{port}[/yellow][/green]")
        
        subprocess.run(
            ["uvicorn", "nexy-config:run", "--host", host, "--port", str(port), "--reload", "--log-level", "debug"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start server: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")

def add(package: str):
    """Ajoute un package en utilisant le pip de l'environnement virtuel nexy_env"""
    try:
        if path.exists("nexy_env"):
            pip_path = "nexy_env/Scripts/pip" if platform == "win32" else "nexy_env/bin/pip"
            subprocess.run([pip_path, "install", package], check=True)
        else:
            subprocess.run(["pip", "install", package], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to install package {package}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while installing {package}: {e}")

