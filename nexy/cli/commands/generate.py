"""
Author: Espoir Loém

This module provides functionality for generating new components (controller, service, model) via the command line interface.
"""

from os import makedirs, path
from typer import Argument, Exit
from rich.prompt import Confirm

from nexy.cli.core.constants import CMD, Console
from nexy.cli.core.utils import generate_controller, generate_model, generate_service, print_banner

RESOURCE_GENERATORS = {
    "controller": (generate_controller, "app/{name}", "controller.py"),
    "co": (generate_controller, "app/{name}", "controller.py"),
    "service": (generate_service, "app/{name}", "service.py"),
    "s": (generate_service, "app/{name}", "service.py"),
    "model": (generate_model, "app/{name}", "model.py"),
    "mo": (generate_model, "app/{name}", "model.py"),
}

def validate_resource(resource: str):
    """Validates if the resource type is supported."""
    if resource not in RESOURCE_GENERATORS:
        Console.print(f"[red]❌ Invalid resource type. Available options: {', '.join(RESOURCE_GENERATORS.keys())}[/red]")
        raise Exit(1)

def check_project_directory():
    """Checks if the current directory is a Nexy project."""
    if not path.exists("app"):
        Console.print("[red]❌ You must be in a Nexy project to generate components.[/red]")
        raise Exit(1)

def create_file(generator_func, file_path, name):
    """Creates the file for the resource."""
    if path.exists(file_path):
        overwrite = Confirm.ask(
            f"[yellow]⚠️  {file_path} already exists. Do you want to overwrite it?[/yellow]"
        )
        if not overwrite:
            Console.print("[yellow]Generation cancelled.[/yellow]")
            raise Exit(0)

    with open(file_path, "w") as f:
        f.write(generator_func(name))
    Console.print(f"[green]✨ {file_path} generated successfully![/green]")

@CMD.command()
def generate(
    resource: str = Argument(..., help="Type of resource to generate (controller/service/model)"),
    name: str = Argument(..., help="Name of the resource")
):
    """Generates a new component (controller, service, model)."""
    print_banner()
    validate_resource(resource)
    check_project_directory()

    generator_func, base_path, file_template = RESOURCE_GENERATORS[resource]
    makedirs(base_path, exist_ok=True)
    file_path = path.join(base_path, file_template.format(name=name.lower()))
    create_file(generator_func, file_path, name)

@CMD.command()
def g(
    resource: str = Argument(..., help="Type of resource to generate (shortcut for generate)"),
    name: str = Argument(..., help="Name of the resource")
):
    """Shortcut alias for generate."""
    generate(resource=resource, name=name)
