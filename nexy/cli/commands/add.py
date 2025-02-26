"""
Author: Espoir Loém

This module provides functionality for adding a package to a Nexy project via the command line interface.
"""

from subprocess import run, CalledProcessError
from os import path
from typer import Argument, Exit
from rich.progress import Progress, SpinnerColumn, TextColumn

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import print_banner

@CMD.command()
def add(
    package: str = Argument(..., help="Package to add to the project")
):
    """Adds a dependency to the project."""
    print_banner()
    
    if not path.exists("requirements.txt"):
        Console.print("[yellow]⚠️  requirements.txt file not found. Creating...[/yellow]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(f"[green]Installing {package}...", total=None)
            print("\n")
            run(["pip", "install", package], check=True)
            
            # Update requirements.txt
            run(["pip", "freeze"], stdout=open("requirements.txt", "w"), check=True)
            
        Console.print(f"[green]✨ Package {package} installed and added to requirements.txt[/green]\n")
    except CalledProcessError as e:
        Console.print(f"[red]❌ Error during installation: {str(e)}[/red]")
        raise Exit(1)
