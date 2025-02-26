"""
Author: Espoir Loém

This module provides functionality for serving Nexy applications via the command line interface.
"""

import logging
import subprocess
from os import system, path
from sys import platform
import typer
from rich.prompt import IntPrompt

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import get_next_available_port, print_banner

@CMD.command()
def serve(
    port: int = typer.Option(3000, "--port", "-p", help="Server port"),
    host: str = typer.Option("localhost", "--host", help="Server host"),
    worker: int = typer.Option(1, help="Number of workers")
) -> None:
    """Starts the server."""
    port = get_next_available_port(port)
    print_banner()
    Console.print(f"[green]Server started on [yellow]http://{host}:{port}[/yellow][/green]")
    
    command = f"uvicorn nexy-config:run --host {host} --port {port} --reload --log-level debug"
    system(command)

def add(package: str):
    """Installs a package using the virtual environment's pip."""
    pip_path = "nexy_env/Scripts/pip" if platform == "win32" else "nexy_env/bin/pip"
    if path.exists("nexy_env"):
        system(f"{pip_path} install {package}")
    else:
        system(f"pip install {package}")
