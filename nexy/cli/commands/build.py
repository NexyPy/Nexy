"""
Author: Espoir Loém

This module provides functionality for building Nexy projects via the command line interface.
"""

import subprocess
import logging
from os import path, environ
from sys import platform
from typer import Option, Argument
from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import print_banner

logging.basicConfig(level=logging.INFO)

def activate_virtualenv():
    """Activate the virtual environment if not already activated."""
    if 'VIRTUAL_ENV' in environ:
        return

    venv_path = "venv/Scripts/activate" if platform == "win32" else "venv/bin/activate"
    if path.exists(venv_path):
        logging.info("Activating virtual environment...")
        activate_command = f"source {venv_path}" if platform != "win32" else venv_path
        subprocess.run(activate_command, shell=True, check=True)
    else:
        logging.error("Virtual environment not found. Please create it first.")
        raise SystemExit(1)

@CMD.command()
def build(
    output_dir: str = Option("dist", "--output-dir", "-o", help="Output directory for the build"),
    clean: bool = Option(False, "--clean", help="Clean the output directory before building")
):
    """Builds the Nexy project."""
    try:
        activate_virtualenv()
        print_banner()
        
        if clean and path.exists(output_dir):
            logging.info(f"Cleaning output directory: {output_dir}")
            subprocess.run(["rm", "-rf", output_dir], check=True)
        
        logging.info("Building the project...")
        subprocess.run(["python", "setup.py", "sdist", "bdist_wheel", "--dist-dir", output_dir], check=True)
        Console.print(f"[green]Build completed successfully! Output directory: {output_dir}[/green]")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to build the project: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
