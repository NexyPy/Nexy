"""
Author: Espoir Loém

This module provides functionality for creating new Nexy projects via the command line interface.
It includes the ProjectManager class, which handles project creation, configuration, and success messaging.
"""

from os import path
from sys import platform
from typing import Optional
from typing_extensions import Annotated
from typer import Argument
from InquirerPy import inquirer
from rich.prompt import Prompt

from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.models import ORM, Database, ProjectType, TestFramework
from nexy.cli.core.project_builder import ProjectBuilder
from pathlib import Path

class ProjectManager:
    def __init__(self, project_name: Optional[str] = None):
        self.project_name = project_name
        self.builder = None

    def print_success_message(self, test_framework: TestFramework):
        """Displays a success message after project creation."""
        activation_command = "./nexy_env/Scripts/activate" if platform == "win32" else "source nexy_env/bin/activate"
        success_message = f"[bold green]✨ Project created successfully![/bold green]\n\nTo get started:\n[yellow]cd {self.project_name}\n{activation_command}\nnexy dev\n[/yellow]"

        if test_framework != TestFramework.NONE:
            test_commands = {
                TestFramework.PYTEST: "pytest",
                TestFramework.UNITTEST: "python -m unittest discover tests",
                TestFramework.ROBOT: "robot tests/",
            }
            success_message += f"To run tests:\n[yellow]{test_commands[test_framework]}[/yellow]\n"

        Console.print(success_message)

    def collect_project_options(self):
        """Collects project configuration options via prompts."""
        
        # Project Type
        project_type = ProjectType(inquirer.select(
            message="🤔 Starter kit: ",
            choices=[t.value for t in ProjectType],
            default=ProjectType.MICROSERVICE.value
        ).execute())
        self.builder.set_project_type(project_type)

        if project_type == ProjectType.WEBAPP:
            self.configure_webapp_options()

        # Database
        template_engine = Database(inquirer.select(
            message="Which database would you like to use: ",
            choices=[db.value for db in Database],
            default=Database.MYSQL.value
        ).execute())
        self.builder.set_database(template_engine)
        
        # ORM
        if template_engine != Database.NONE:
            orm = ORM(inquirer.select(
                message="Which ORM would you like to use: ",
                choices=[orm.value for orm in ORM],
                default=ORM.PRISMA.value
            ).execute())
            self.builder.set_orm(orm)

        # Test Framework
        test_framework = TestFramework(inquirer.select(
            message="Test framework to use:",
            choices=[tf.value for tf in TestFramework],
            height=20,
            default=TestFramework.PYTEST.value
        ).execute())
        self.builder.set_test_framework(test_framework)

        # Additional Features
        # self.builder.add_feature("validation")
        # if inquirer.confirm(message="Voulez-vous ajouter le support CORS?").execute():
        #     self.builder.add_feature("cors")
        # if project_type == ProjectType.MICROSERVICE and inquirer.confirm(
        #     message="Voulez-vous ajouter la documentation Swagger?"
        # ).execute():
        #     self.builder.add_feature("swagger")

    def configure_webapp_options(self):
        """Configures options specific to webapp projects."""
        template_engine = Database(inquirer.select(
            message="Which database would you like to use: ",
            choices=[db.value for db in Database],
            default=Database.MYSQL.value
        ).execute())
        self.builder.set_database(template_engine)
        if inquirer.confirm(message="Would you like to use Tailwind CSS?").execute():
            self.builder.add_feature("tailwind")

    def verify_project_name(self) -> str:
        """
        Checks if the project name is already in use.
        If so, asks the user if they want to choose a different name.
        Returns the validated project name or None if the user cancels.
        """
        while True:
            if not self.project_name:
                self.project_name = Console.input("✅ What is your project named?... ")
            else:
                Console.print(f"✅ Project name: [green]{self.project_name}[/green]\n")

            if path.isdir(self.project_name):
                Console.print(f"[red]❌ This project name already exists.[/red]")
                if not inquirer.confirm(
                    message="Do you want to choose a different name?...",
                    qmark="🤔",
                    default=True
                ).execute():
                    return None
                self.project_name = None
            else:
                return self.project_name

    def create_project(self):
        """Common function to create a new project."""
        from nexy.cli.core.utils import print_banner
        
        print_banner()
        
        name = self.verify_project_name()
        if name is None:
            return None

        self.builder = ProjectBuilder(name)
        self.collect_project_options()

        Console.print("\n[bold green]Creating project...[/bold green]")
        self.builder.build()

        self.print_success_message(self.builder.test_framework)

@CMD.command()
def new(project_name: Annotated[Optional[str], Argument(..., help="Project name")] = None):
    """Creates a new Nexy project."""
    manager = ProjectManager(project_name)
    manager.create_project()

@CMD.command()
def n(project_name: Annotated[Optional[str], Argument(..., help="Project name")] = None):
    """Alias for the new command."""
    manager = ProjectManager(project_name)
    manager.create_project()
