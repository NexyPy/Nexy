from os import makedirs, path
from typer import Argument, Exit
from rich.prompt import  Confirm

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

# [Previous CLI commands remain the same until generate]

@CMD.command()
def generate(
    resource: str = Argument(..., help="Type de ressource à générer (controller/service/model)"),
    name: str = Argument(..., help="Nom de la ressource")
):
    """Génère un nouveau composant (controller, service, model)"""
    print_banner()
    
    if resource not in RESOURCE_GENERATORS:
        Console.print(f"[red]❌ Type de ressource invalide. Choix possibles: {', '.join(RESOURCE_GENERATORS.keys())}[/red]")
        raise Exit(1)
    
    generator_func, base_path, file_template = RESOURCE_GENERATORS[resource]
    
    # Vérifier si nous sommes dans un projet Nexy
    if not path.exists("app"):
        Console.print("[red]❌ Vous devez être dans un projet Nexy pour générer des composants.[/red]")
        raise Exit(1)
    
    # Créer le répertoire s'il n'existe pas
    makedirs(base_path, exist_ok=True)
    
    # Générer le fichier
    file_path = path.join(base_path, file_template.format(name=name.lower()))
    
    if path.exists(file_path):
        overwrite = Confirm.ask(
            f"[yellow]⚠️  {resource.capitalize()} {name} existe déjà. Voulez-vous l'écraser?[/yellow]"
        )
        if not overwrite:
            Console.print("[yellow]Génération annulée.[/yellow]")
            raise Exit(0)
    
    with open(file_path, "w") as f:
        f.write(generator_func(name))
    
    Console.print(f"[green]✨ {resource.capitalize()} {name} généré avec succès dans {file_path}[/green]")

@CMD.command()
def g(
    resource: str = Argument(..., help="Type de ressource à générer (raccourci pour generate)"),
    name: str = Argument(..., help="Nom de la ressource")
):
    """Alias raccourci pour generate"""
    generate(resource=resource, name=name)
