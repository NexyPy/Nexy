
"""
Author: Espoir Loémba

This module provides functionality for initializing a new Nexy project via the command line interface.
"""

import os
import subprocess
from pathlib import Path
from typing_extensions import Annotated
from typer import Argument, Option
from typing import Optional
from nexy.cli.core.constants import Console, CMD

@CMD.command()
def init(
    project_name: Annotated[Optional[str], Argument(..., help="Project name")] = None,
    template: Annotated[Optional[str], Option(None, "--template", "-t", help="Project template")] = None
):
    """
    Initializes a new Nexy project.
    """
    if not project_name:
        project_name = Console.input("✅ What is your project named?... ")

    project_path = Path(project_name)
    if project_path.exists():
        Console.print(f"[red]❌ The project directory '{project_name}' already exists.[/red]")
        return

    try:
        # Create project directory
        project_path.mkdir(parents=True, exist_ok=False)
        Console.print(f"[green]✨ Created project directory: {project_name}[/green]")

        # Optionally, clone a template repository
        if template:
            subprocess.check_call(["git", "clone", template, str(project_path)])
            Console.print(f"[green]✨ Cloned template from {template}[/green]")
        else:
            # Create a basic project structure
            (project_path / "main.py").write_text("# Your Nexy project starts here\n")
            Console.print(f"[green]✨ Created basic project structure[/green]")

        Console.print(f"[bold green]✨ Project '{project_name}' initialized successfully![/bold green]")
    except Exception as e:
        Console.print(f"[red]❌ Error initializing project: {e}[/red]")
