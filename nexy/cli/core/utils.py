"""
Author: Espoir Loém
"""

import importlib
from os import makedirs, name, path
import subprocess
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket
import sys
from time import sleep
from typing import List
from rich.columns import Columns
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from typer import Exit, echo

from nexy.cli.core.constants import Console
from nexy.cli.core.models import ORM, Database, ProjectType, TestFramework


def print_banner():
    Console.print(
"""
[green]
       _   __                
      / | / /__  _  ____  __
     /  |/ / _ \| |/_/ / / /
    / /|  /  __/>  </ /_/ / 
   /_/ |_/\___/_/|_|\__, /  
                   /____/   
[/green]
"""
)


# Fonctions utilitaires pour la gestion des ports
def is_port_in_use(port: int, host: str = 'http://localhost') -> bool:
    with socket(AF_INET, SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except OSError:
            return True

def find_available_port(start_port: int = 3000, host: str = 'http://localhost') -> list[int]:
    available_ports = []
    current_port = start_port
    while len(available_ports) < 5 and current_port < 65535:
        if not is_port_in_use(current_port, host):
            available_ports.append(current_port)
        current_port += 1
    return available_ports

def display_port_choices(available_ports: list[int], host: str) -> None:
    panels = []
    for i, port in enumerate(available_ports, 1):
        panel_content = f"[bold]Port {port}[/bold]\n{host}:{port}"
        color = ["green", "blue", "yellow", "cyan", "magenta"][i - 1]
        panels.append(Panel(
            panel_content,
            title=f"Choix {i}",
            border_style=color,
            padding=1
        ))
    Console.print(Columns(panels))


# Fonctions de génération de fichiers
def generate_requirements(project_type: ProjectType, database: Database, orm: ORM, 
                        test_framework: TestFramework, features: List[str]) -> str:
    requirements = [
        "nexy",
        "uvicorn",
        "python-dotenv",
        "inquirerpy==0.3.4"
    ]
    
    if database != Database.NONE:
        db_requirements = {
            Database.MYSQL: ["mysql-connector-python"],
            Database.POSTGRESQL: ["psycopg2-binary"],
            Database.MONGODB: ["motor"],
            Database.SQLITE: [],
        }
        requirements.extend(db_requirements.get(database, []))
    
    if orm != ORM.NONE:
        orm_requirements = {
            ORM.PRISMA: ["prisma"],
            ORM.SQLALCHEMY: ["sqlalchemy"],
        }
        requirements.extend(orm_requirements.get(orm, []))
    
    if test_framework != TestFramework.NONE:
        test_requirements = {
            TestFramework.PYTEST: ["pytest", "pytest-cov", "pytest-asyncio"],
            TestFramework.UNITTEST: ["unittest2"],
            TestFramework.ROBOT: ["robotframework"],
        }
        requirements.extend(test_requirements.get(test_framework, []))
    
    if project_type == ProjectType.DEFAULT:
        requirements.extend(["jinja2"])
    
    if "auth" in features:
        requirements.extend(["python-jose[cryptography]", "passlib[bcrypt]"])
    
    return "\n".join(requirements)

def generate_env_file(database: Database) -> str:
    env_vars = [
        "APP_ENV=development",
        "SECRET_KEY=your-secret-key-here",
    ]
    
    db_vars = {
        Database.MYSQL: ["DATABASE_URL=mysql://user:password@localhost:3306/dbname"],
        Database.POSTGRESQL: ["DATABASE_URL=postgresql://user:password@localhost:5432/dbname"],
        Database.MONGODB: ["DATABASE_URL=mongodb://localhost:27017/dbname"],
        Database.SQLITE: ["DATABASE_URL=sqlite:///./sql_app.db"],
    }
    
    if database != Database.NONE:
        env_vars.extend(db_vars.get(database, []))
    # 
    return "\n".join(env_vars)

def create_test_config(project_name: str, test_framework: TestFramework):
    if test_framework == TestFramework.PYTEST:
        pytest_ini = "[pytest]\ntestpaths = tests\npython_files = test_*.py\npython_classes = Test\npython_functions = test_*\naddopts = -v --cov=app"
        with open(path.join(project_name, "pytest.ini"), "w") as f:
            f.write(pytest_ini)
            
        test_example = """import pytest\nfrom fastapi.testclient import TestClient\nfrom main import app\n\nclient = TestClient(app)\n\ndef test_read_main():\n    response = client.get("/")\n    assert response.status_code == 200"""
        makedirs(path.join(project_name, "tests"), exist_ok=True)
        with open(path.join(project_name, "tests", "test_main.py"), "w") as f:
            f.write(test_example)

    elif test_framework == TestFramework.ROBOT:
        robot_test = """*** Settings ***\nDocumentation Example Test Suite\nLibrary RequestsLibrary\n\n*** Test Cases ***\nTest Main Page\n Create Session app http://localhost:3000\n ${response}= GET On Session app /\n Status Should Be 200 ${response}"""
        makedirs(path.join(project_name, "tests"), exist_ok=True)
        with open(path.join(project_name, "tests", "main.robot"), "w") as f:
            f.write(robot_test)

def setup_virtualenv(project_name: str, env_name: str, requirements_file: str = None):
    """Set up a virtual environment and install dependencies.
    
    Args:
        project_name: Name of the project directory
        env_name: Name of the virtual environment
        requirements_file: Optional path to requirements.txt file
    """
    try:
        venv_path = path.join(project_name, env_name)
        
        # Check if environment already exists
        if path.exists(venv_path):
            Console.print(f"[yellow]L'environnement {env_name} existe déjà.[/yellow]")
            return

        # Create virtual environment
        Console.print(f"[blue]Création de l'environnement virtuel {env_name}...[/blue]")
        result = subprocess.run(
            [sys.executable, '-m', 'venv', venv_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Get pip path based on OS
        pip_executable = path.join(venv_path, 'Scripts', 'pip.exe') if sys.platform == "win32" else path.join(venv_path, 'bin', 'pip')
        python_executable = path.join(venv_path, 'Scripts', 'python.exe') if sys.platform == "win32" else path.join(venv_path, 'bin', 'python')
        
        # Upgrade pip using python -m pip to avoid permission issues
        Console.print("[bold yellow]Mise à jour de pip...[/bold yellow]")
        subprocess.run([python_executable, '-m', 'pip', 'install', '--upgrade', 'pip'], check=True)

        # Install dependencies if requirements file exists
        if requirements_file:
            Console.print(f"[bold yellow]Installation des dépendances depuis {requirements_file}...[/bold yellow]")
            subprocess.run([pip_executable, 'install', '-r', requirements_file], check=True)
            Console.print(f"[green]✓ Dépendances installées avec succès[/green]")

        Console.print(f"[green]✓ Environnement virtuel {env_name} créé avec succès[/green]")

    except subprocess.CalledProcessError as e:
        Console.print(f"[red]Erreur lors de l'exécution de la commande : {e.stderr}[/red]")
        raise Exit(1)
    except Exception as e:
        Console.print(f"[red]Une erreur est survenue : {str(e)}[/red]")
        raise Exit(1)



def create_project_structure(
    project_name: str,
    project_type: ProjectType,
    database: Database,
    orm: ORM,
    test_framework: TestFramework,
    features: List[str]
):
    base_dirs = [
        "",
        "app",
        "public",
        "tests",
    ]
    
    if project_type == ProjectType.WEBAPP:
        base_dirs.extend(["src/components/","src/utils/"])
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task("[green]Création de la structure du projet...[/green]", total=None)
        
        for dir_path in base_dirs:
            full_path = path.join(project_name, dir_path)
            makedirs(full_path, exist_ok=True)
            sleep(0.1)
        
        # Check if git is installed and initialize a git repository
        if subprocess.run(["git", "--version"], capture_output=True, text=True).returncode == 0:
            subprocess.run(["git", "init", project_name], check=True)
        else:
            Console.print("[red]Git n'est pas installé. Veuillez installer Git pour initialiser un dépôt.[/red]")

        if project_type == ProjectType.DEFAULT:
            files_to_create = {
                "nexy-config.py":"""from nexy import Nexy\nrun = Nexy()\n""",
                "app/controller.py": """from nexy import component\n\n@component(\n   imports=[]\n)\ndef Layout(children):\n\treturn {"children":children}\n@component(\n   imports=[]\n)\ndef View():\n\treturn {"name": "hello world"}""",
                "app/view.html":"generate_view()",
                "app/Layout.html":" ",
                "requirements.txt": generate_requirements(project_type, database, orm, test_framework, features),
                ".env": generate_env_file(database),
                "README.md": generate_readme(project_name, project_type, database, orm, test_framework, features),
            }
        else:
            files_to_create = {
                "nexy-config.py":"""from nexy import Nexy\nrun = Nexy()\n""",
                "app/controller.py": """async def GET():\n\treturn {"name": "hello world"}\nasync def POST():\n\treturn {"name": "hello world"}""",
                "requirements.txt": generate_requirements(project_type, database, orm, test_framework, features),
                ".env": generate_env_file(database),
                ".gitignore": "# Virtual environment\nvenv\n# Python cache\n__pycache__\n# Compiled files\n*.pyc\n",
                "README.md": generate_readme(project_name, project_type, database, orm, test_framework, features),
        }

        for file_name, content in files_to_create.items():
            with open(path.join(project_name, file_name), "w") as f:
                f.write(content)
            sleep(0.1)
        
        if test_framework != TestFramework.NONE:
            create_test_config(project_name, test_framework)

def generate_readme(project_name: str, project_type: ProjectType, database: Database, 
                   orm: ORM, test_framework: TestFramework, features: List[str]) -> str:
    testing_section = ""
    if test_framework != TestFramework.NONE:
        testing_commands = {
            TestFramework.PYTEST: "pytest",
            TestFramework.UNITTEST: "python -m unittest discover tests",
            TestFramework.ROBOT: "robot tests/",
        }
        test_command = testing_commands.get(test_framework, "")
        testing_section = f"## Tests\nPour exécuter les tests :\n```bash\n{test_command}\n```\n"

    return f"# {project_name}\n\n## Description\nProjet {project_type.value} généré avec Nexy CLI\n\n## Configuration technique\n- Type: {project_type.value}\n- Base de données: {database.value}\n- ORM: {orm.value}\n- Framework de test: {test_framework.value}\n- Fonctionnalités: {', '.join(features)}\n\n## Installation\n\n1. Cloner le projet\n```bash\ngit clone <url-du-projet>\ncd {project_name}\n```\n\n2. Installer les dépendances\n```bash\nnexy install\n```\n\n4. Lancer le serveur de développement\n```bash\nnexy dev\n```\n{testing_section}\n"

# Nouvelles fonctions pour la génération de composants
def generate_controller(name: str) -> str:
    return f"""
    async def GET():
        return {{"message": "Welcome to {name} controller"}}
    
    async def POST():
        return {{"message": "Welcome to {name} controller"}}
    
    async def PUT():
        return {{"message": f"Updated {name} {{id}}", "data": data}}
    
    async def DELETE():
        return {{"message": f"Deleted {name} {{id}}"}}
"""

def generate_service(name: str) -> str:
    return f"""class {name.capitalize()}Service:
    def __init__(self):
        # Initialize your service
        pass
    
    async def get_all(self):
        # Implement get all logic
        pass
    
    async def get_by_id(self, id: int):
        # Implement get by id logic
        pass
    
    async def create(self, data: dict):
        # Implement create logic
        pass
    
    async def update(self, id: int, data: dict):
        # Implement update logic
        pass
    
    async def delete(self, id: int):
        # Implement delete logic
        pass
"""

def generate_model(name: str) -> str:
    return f"""from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from nexy.app import Base

class {name.capitalize()}(Base):
    __tablename__ = "{name.lower()}s"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {{
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }}
"""

def generate_component(name: str) -> str:
    component_name = name[0].capitalize() + name[1:]
    return f"""
    from nexy import Component
    @Component(imports=[])
    def {component_name}(name: str):
        return {{
            "message": f"Welcome  {{name}}"
        }}
    """

def is_port_in_use(port: int, host: str = "localhost") -> bool:
    """Vérifie si un port est déjà utilisé sur l'hôte."""
    with socket(AF_INET, SOCK_STREAM) as s:
        result = s.connect_ex((host, port))
        return result == 0  # Si le résultat est 0, cela signifie que le port est utilisé

def get_next_available_port(starting_port: int = 3000, host: str = "localhost") -> int:
    """Trouve un port disponible à partir d'un port de départ."""
    port = starting_port
    while is_port_in_use(port, host):
        port += 1
    return port
