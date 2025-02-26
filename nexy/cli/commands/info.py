"""
Author: Espoir Loém

This module provides functionality for displaying project information via the command line interface.
"""

from os import popen, path, getenv
from sys import version
from rich.table import Table

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import print_banner


@CMD.command()
def info():
    """Displays project information."""
    print_banner()

    table = Table(title="Project Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="magenta")

    project_info = None
    if path.exists("pyproject.toml"):
        with open("pyproject.toml", "r") as f:
            project_info = f.read()

    table.add_row("Python Version", version.split()[0])
    table.add_row("Nexy Version", "1.0.0")
    table.add_row("Environment", getenv("NEXY_ENV", "development"))

    git_branch = popen("git branch --show-current").read().strip() if path.exists(".git") else "N/A"
    table.add_row("Git Branch", git_branch)

    deps = "N/A"
    if path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            deps = str(len(f.readlines()))
    table.add_row("Dependencies", deps)

    Console.print(table)
