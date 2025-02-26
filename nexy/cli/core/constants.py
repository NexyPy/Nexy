"""
Author: Espoir Loém

This module defines the core constants used across the Nexy CLI.
"""

from rich.console import Console
from typer import Typer

# Initialize the console for rich text output
Console = Console()

# Initialize the Typer application with a help message
CMD = Typer(help="Nexy CLI - Framework de développement web moderne pour Python")

