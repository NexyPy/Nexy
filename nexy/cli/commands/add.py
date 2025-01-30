from os import system, path
from typer import Argument,Exit
from rich.progress import Progress, SpinnerColumn, TextColumn
import sys

from nexy.cli.core.constants import Console,CMD
from nexy.cli.core.utils import print_banner



@CMD.command()
def add(
    package: str = Argument(..., help="Package à ajouter au projet")
):
    """Ajoute une dépendance au projet"""
    print_banner()
    
    if not path.exists("requirements.txt"):
        Console.print("[yellow]⚠️  Fichier requirements.txt non trouvé. Création...[/yellow]\n")
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[green]Installation de {package}...", total=None)
            print("\n")
            system(f"pip install {package}")
            
            # Mettre à jour requirements.txt
            system(f"pip freeze > requirements.txt")
            
        Console.print(f"[green]✨ Package {package} installé et ajouté à requirements.txt[/green]\n")
    except Exception as e:
        Console.print(f"[red]❌ Erreur lors de l'installation: {str(e)}[/red]")
        raise Exit(1)
