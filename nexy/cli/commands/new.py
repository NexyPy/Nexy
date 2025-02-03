from os import path
from sys import platform
from typing import Optional
from click import prompt
from typing_extensions import Annotated
from typer import Argument
from InquirerPy import inquirer
from rich.prompt import Prompt


from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.models import ORM, Database, ProjectType, TestFramework
from nexy.cli.core.project_builder import ProjectBuilder
from InquirerPy.validator import Validator, ValidationError
from pathlib import Path


def print_success_message(project_name: str, test_framework: TestFramework):
    """Affiche le message de succès après la création du projet"""
    success_message = f"""
[bold green]✨ Projet créé avec succès![/bold green]

Pour démarrer:
[yellow]cd {project_name}
{"./nexy_env/Scripts/activate" if platform == "win32" else "source nexy_env/bin/activate"}
nexy dev
[/yellow]
"""

    if test_framework != TestFramework.NONE:
        test_commands = {
            TestFramework.PYTEST: "pytest",
            TestFramework.UNITTEST: "python -m unittest discover tests",
            TestFramework.ROBOT: "robot tests/",
        }
        success_message += f"""
Pour lancer les tests:
[yellow]{test_commands[test_framework]}[/yellow]
"""

    Console.print(success_message)




def collect_project_options(builder: ProjectBuilder):
    """Collecte les options de configuration du projet via des prompts"""
    
    # Project Type
    project_type = ProjectType(inquirer.select(
        message="🤔 Started kit: ",
        choices=[t.value for t in ProjectType],
        default=ProjectType.MICROSERVICE.value
    ).execute())
    builder.set_project_type(project_type)

    if project_type == ProjectType.WEBAPP :
        template_engine = Database(inquirer.select(
            message="Which database would you like to use: ",
            choices=[db.value for db in Database],
            default=Database.MYSQL.value
        ).execute())
        builder.set_database(template_engine)
        if  inquirer.confirm(message="Voulez-vous utiliser Tailwind CSS?").execute():
            builder.add_feature("tailwind")
    # Database

    template_engine = Database(inquirer.select(
        message="Which database would you like to use: ",
        choices=[db.value for db in Database],
        default=Database.MYSQL.value
    ).execute())
    builder.set_database(template_engine)
    
    # ORM
    if template_engine != Database.NONE:
        orm = ORM(inquirer.select(
            message="Which ORM would you like to use: ",
            choices=[orm.value for orm in ORM],
            default=ORM.PRISMA.value
        ).execute())
        builder.set_orm(orm)

    # Test Framework
    test_framework = TestFramework(inquirer.select(
        message="Framework de test à utiliser:",
        choices=[tf.value for tf in TestFramework],
        height=20,
        default=TestFramework.PYTEST.value
    ).execute())
    builder.set_test_framework(test_framework)

    # Features
    if inquirer.confirm(message="Voulez-vous ajouter l'authentification?").execute():
        builder.add_feature("auth")
    if inquirer.confirm(message="Voulez-vous ajouter la validation des données?").execute():
        builder.add_feature("validation")
    if inquirer.confirm(message="Voulez-vous ajouter le support CORS?").execute():
        builder.add_feature("cors")
    if project_type == ProjectType.API and inquirer.confirm(
        message="Voulez-vous ajouter la documentation Swagger?"
    ).execute():
        builder.add_feature("swagger")


from os import path
from InquirerPy import inquirer
from nexy.cli.core.constants import Console  # Assurez-vous que Console est bien importé

def verify_project_name(project_name: str) -> str:
    """
    Vérifie si le nom de projet est déjà utilisé.
    Si oui, demande à l'utilisateur s'il souhaite choisir un autre nom.
    Retourne le nom de projet validé ou None si l'utilisateur annule.
    """
    while True:  # Boucle jusqu'à ce qu'un nom unique soit saisi ou que l'utilisateur annule
        if not project_name:
            project_name = Console.input("✅ What is your project named ?... ")
        else:
            Console.print(f"✅ Project name: [green]{project_name}[/green]\n")

        if path.isdir(project_name):
            Console.print(f"[red]❌ This project name already exists.[/red]")
            # Proposer à l'utilisateur de choisir un autre nom
            if not inquirer.confirm(
                message="Do you want to choose a different name ?...",
                qmark= "🤔",
                default=True
            ).execute():
                return None  # L'utilisateur a choisi de ne pas continuer
            # Réinitialiser le nom de projet pour forcer une nouvelle saisie
            project_name = None
        else:
            return project_name

        
def create_project(project_name: Optional[str] = None):
    """Fonction commune pour créer un nouveau projet"""
    from nexy.cli.core.utils import print_banner
    
    print_banner()
    
    
    
    name = verify_project_name(project_name)
    if name is None:
        return None


    # Créer et configurer le projet
    builder = ProjectBuilder(name)
    collect_project_options(builder)

    # Construire le projet
    Console.print("\n[bold green]Création du projet...[/bold green]")
    builder.build()

    # Afficher le message de succès
    print_success_message(project_name, builder.test_framework)




@CMD.command()
def new(project_name: Annotated[Optional[str], Argument(..., help="Nom du projet")] = None):
    """Crée un nouveau projet Nexy"""
    create_project(project_name)

@CMD.command()
def n(project_name: Annotated[Optional[str], Argument(..., help="Nom du projet")] = None):
    """Alias pour la commande new"""
    create_project(project_name)
