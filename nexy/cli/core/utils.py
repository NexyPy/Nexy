import importlib
from os import makedirs, name, path
import subprocess
from pathlib import Path
from socket import AF_INET, SOCK_STREAM, socket
import sys
from time import sleep
from typing import  List
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
    
    if project_type == ProjectType.WEBAPP:
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
        pytest_ini = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test
python_functions = test_*
addopts = -v --cov=app
"""
        with open(path.join(project_name, "pytest.ini"), "w") as f:
            f.write(pytest_ini)
            
        test_example = """import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
"""
        makedirs(path.join(project_name, "tests"), exist_ok=True)
        with open(path.join(project_name, "tests", "test_main.py"), "w") as f:
            f.write(test_example)

    elif test_framework == TestFramework.ROBOT:
        robot_test = """*** Settings ***
Documentation     Example Test Suite
Library           RequestsLibrary

*** Test Cases ***
Test Main Page
    Create Session    app    http://localhost:3000
    ${response}=    GET On Session    app    /
    Status Should Be    200    ${response}
"""
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
        "config"
    ]
    
    if project_type == ProjectType.WEBAPP:
        base_dirs.extend(["app/templates", "app/static", "app/static/css", "app/static/js"])
    
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
        
        files_to_create = {
            "app/controller.py": """
async def GET():
    return {"name": "hello world"}
""",
            "requirements.txt": generate_requirements(project_type, database, orm, test_framework, features),
            ".env": generate_env_file(database),
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
        testing_section = f"""
## Tests
Pour exécuter les tests :
```bash
{test_command}
```
"""

    return f"""# {project_name}

## Description
Projet {project_type.value} généré avec Nexy CLI

## Configuration technique
- Type: {project_type.value}
- Base de données: {database.value}
- ORM: {orm.value}
- Framework de test: {test_framework.value}
- Fonctionnalités: {', '.join(features)}

## Installation

1. Cloner le projet
```bash
git clone <url-du-projet>
cd {project_name}
```

2. Installer les dépendances
```bash
pip install -r requirements.txt
```

3. Configurer les variables d'environnement
```bash
cp .env.example .env
# Modifier les variables dans .env
```

4. Lancer le serveur de développement
```bash
python main.py
```
{testing_section}
"""

# [Previous imports and code until the CLI commands remain the same...]

# Nouvelles fonctions pour la génération de composants
def generate_controller(name: str) -> str:
    return f"""from nexy.app import Controller

class {name.capitalize()}Controller(Controller):
    def __init__(self):
        super().__init__()
    
    async def index(self):
        return {{"message": "Welcome to {name} controller"}}
    
    async def get_by_id(self, id: int):
        return {{"id": id, "name": "{name}"}}
    
    async def create(self, data: dict):
        return {{"message": f"Created {name}", "data": data}}
    
    async def update(self, id: int, data: dict):
        return {{"message": f"Updated {name} {{id}}", "data": data}}
    
    async def delete(self, id: int):
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



def load_config():
    """
    Vérifie si config.py existe à la racine du projet et l'importe dynamiquement.
    """
    # Chemin du répertoire courant
    root_path = Path.cwd()
    
    # Chemin potentiel vers config.py
    config_file = root_path / "config.py"
    
    # Vérifier l'existence de config.py
    if not config_file.exists():
        echo("❌ Le fichier 'config.py' n'a pas été trouvé à la racine du projet.")
        raise Exit(code=1)
    
    # Importer dynamiquement config.py
    try:
        spec = importlib.util.spec_from_file_location("config", config_file)
        config = importlib.util.module_from_spec(spec)
        sys.modules["config"] = config
        spec.loader.exec_module(config)
        return config
    except Exception as e:
        echo(f"❌ Erreur lors du chargement de 'config.py' : {e}")
        raise Exit(code=1)

    




    