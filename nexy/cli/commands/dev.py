"""
Author: Espoir Loémba

This module provides functionality for developing Nexy applications via the command line interface.
"""

import logging
import subprocess
from os import path, environ
from sys import platform
import typer
from rich.prompt import IntPrompt

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import get_next_available_port

logging.basicConfig(level=logging.INFO)

def activate_virtualenv():
    """Activate the virtual environment if not already activated."""
    if 'VIRTUAL_ENV' in environ:
        return

    venv_path = ".venv/Scripts/activate" if platform == "win32" else ".venv/bin/activate"
    if path.exists(venv_path):
        logging.info("Activating virtual environment...")
        activate_command = f"source {venv_path}" if platform != "win32" else venv_path
        subprocess.run(activate_command, shell=True, check=True)
    else:
        logging.error("Virtual environment not found. Please create it first.")
        raise SystemExit(1)

@CMD.command()
def dev(
    port: int = typer.Option(3000, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    worker: int = typer.Option(1, help="Number of workers")
) -> None:
    """Starts the server."""
    try:
        activate_virtualenv()

        port = get_next_available_port(port)
        Console.print(f"[green]Local [yellow]http://{host}:{port}[/yellow][/green]\n")

        subprocess.run(
            ["uvicorn", "nexyconfig:app", "--host", host, "--port", str(port), "--reload", "--log-level", "debug"],
            check=True
        )
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to start server: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")