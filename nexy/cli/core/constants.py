"""
Author: Espoir Loém

This module defines the core constants used across the Nexy CLI.
"""

from rich.console import Console
from typer import Exit, Typer,Option
from nexy import __version__




# Initialize the console for rich text output
Console = Console()

# Initialize the Typer application with a help message
CMD = Typer(
    help="Nexy CLI ",
    context_settings={
        "help_option_names": ["-h", "--help"],
    },
    invoke_without_command=True,
)

def version_callback(value: bool):
    """Print the version of Nexy CLI."""
    if value:
        print(f"Nexy {__version__}")
        raise Exit()


@CMD.callback()
def main(
    version: bool = Option(
        False, 
        "--version", 
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Print version information"
    )
):
    """Nexy CLI - Framework de développement web moderne pour Python"""
    banner = """\n[bold green]Nexy[/bold green] CLI\n"""
    Console.print(banner)


