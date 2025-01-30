from os import popen, path , getenv
from sys import version
from rich.table import Table

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import print_banner


@CMD.command()
def info():
    """Affiche les informations sur le projet"""
    print_banner()
    
    table = Table(title="Information du Projet")
    table.add_column("Propriété", style="cyan")
    table.add_column("Valeur", style="magenta")
    
    try:
        with open("pyproject.toml", "r") as f:
            project_info = f.read()
    except FileNotFoundError:
        project_info = None
    
    table.add_row("Python Version", version.split()[0])
    table.add_row("Nexy Version", "1.0.0")
    table.add_row("Environnement", getenv("NEXY_ENV", "development"))
    
    if path.exists(".git"):
        git_branch = popen("git branch --show-current").read().strip()
        table.add_row("Git Branch", git_branch)
    
    if path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            deps = len(f.readlines())
            table.add_row("Dépendances", str(deps))
    
    Console.print(table)
