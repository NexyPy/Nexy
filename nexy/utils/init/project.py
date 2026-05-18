from __future__ import annotations

import os
import shutil
import subprocess
from contextlib import suppress
from pathlib import Path

from nexy.__version__ import __Version__
from nexy.i18n import t
from nexy.utils.common.console import console

from .clone import GitClone
from .dependencies import DependencyInstaller
from .prompts import ProjectPrompter
from .resolver import TemplateResolver

_MODEL_EXAMPLES: dict[str, str] = {
    "SQLModel": """from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)
""",
    "SQLAlchemy": """from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
""",
    "Tortoise-ORM": """from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    email = fields.CharField(max_length=100, unique=True)
""",
}

_GITIGNORE_CONTENT = """__pycache__/
*.pyc
.env
.nexy/
nexy.db
*.db
node_modules/
dist/
.venv/
venv/
"""


class InitProject:
    """Orchestrates the project initialization process."""

    def __init__(self) -> None:
        self.version = __Version__().get()

    def run(
        self,
        template: str | None = None,
        project_dir: str | None = None,
        command: str = "init",
        show_title: bool = True,
    ) -> None:
        """Main execution flow for project initialization."""
        if project_dir:
            dest = Path(project_dir).resolve()
            dest.mkdir(parents=True, exist_ok=True)
            os.chdir(str(dest))
        else:
            dest = Path(".")

        if show_title:
            title = t("init.title", "nexy {version} {command}").format(
                version=self.version, command=command
            )
            console.print(title)

        already = (
            (dest / "__nexy__").exists()
            or (dest / "nexyconfig.py").exists()
            or (dest / "vite.config.ts").exists()
        )
        if already and not project_dir:
            console.print(
                "[red]nexy[/red] » " + t("init.already", "Project already initialized here")
            )
            return

        if template:
            subdir = f"templates/{template}"
            template_name = template
            config = {"orm": "None", "db_url": None}
        else:
            config = ProjectPrompter().ask_all()
            subdir = TemplateResolver.resolve(config)
            template_name = subdir.replace("templates/", "")

        self._initialize_from_template(subdir, template_name, dest, config)

    def _initialize_from_template(
        self, subdir: str, template_name: str, dest: Path, config: dict | None = None
    ) -> None:
        """Clones and extracts the template into the destination directory."""
        config = config or {}
        orm = config.get("orm", "None")
        db_url = config.get("db_url")
        project_dir_name = dest.name if dest != Path(".") else None
        cloner = GitClone()

        try:
            # Use spinner during initialization
            with console.status(
                "[yellow]nexy[/yellow] » "
                + t("init.initializing", "Initializing {name}...").format(name=template_name),
                spinner="dots",
            ):
                cloner.clone(cloner.repo, cloner.branch, dest, subdir=subdir)

            # Auto-install dependencies
            installer = DependencyInstaller(dest, orm=orm)
            installer.install_all()

            # Generate example model if ORM chosen
            self._generate_model(dest, orm, db_url)

            # Git init + .gitignore
            self._init_git(dest)

            # Final cleanup of build/dist artifacts
            self._cleanup_build_artifacts(dest)

            self._print_success_message(project_dir_name)
        except Exception as e:
            console.print(
                "\n[red]nexy[/red] » "
                + t("init.error", "Initialization failed: {error}").format(error=str(e))
            )
            raise

    def _cleanup_build_artifacts(self, dest: Path) -> None:
        unwanted = ["build", "dist"]
        for folder_name in unwanted:
            folder_path = dest / folder_name
            if folder_path.exists() and folder_path.is_dir():
                shutil.rmtree(folder_path, ignore_errors=True)

    def _generate_model(self, dest: Path, orm: str, db_url: str | None) -> None:
        if orm == "None":
            return
        model_code = _MODEL_EXAMPLES.get(orm)
        if not model_code:
            return
        if db_url:
            model_code = f"# Database: {db_url}\n{model_code}"
        src = dest / "src"
        src.mkdir(parents=True, exist_ok=True)
        (src / "models.py").write_text(model_code)

    def _init_git(self, dest: Path) -> None:
        gitignore = dest / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text(_GITIGNORE_CONTENT)
        with suppress(Exception):
            subprocess.run(
                ["git", "init"],
                cwd=dest,
                check=True,
                capture_output=True,
                shell=os.name == "nt",
            )

    def _print_success_message(self, project_dir_name: str | None = None) -> None:
        console.print(
            "\n[green]nexy[/green] » "
            + t("init.success_title", "Project initialized successfully!")
        )
        console.print("\n" + t("init.next_steps", "Next steps:"))

        step = 1
        if project_dir_name:
            console.print(f"  {step}. [cyan]cd {project_dir_name}[/cyan]")
            step += 1

        console.print(
            f"  {step}. [cyan]nexy dev[/cyan] - "
            + t("init.step_run_dev", "Start the development server")
        )
        console.print(
            f"  {step + 1}. [cyan]nexy --help[/cyan] - "
            + t("init.step_help", "Explore available commands")
        )

        console.print("\n" + t("init.happy_coding", "Happy coding with Nexy!"))
