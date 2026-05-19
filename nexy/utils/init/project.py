from __future__ import annotations

import os
import shutil
import subprocess
from contextlib import suppress
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from nexy.__version__ import __Version__
from nexy.i18n import t
from nexy.utils.common.console import console

from .clone import GitClone
from .dependencies import DependencyInstaller
from .prompts import ProjectPrompter
from .renderer import TemplateRenderer
from .resolver import TemplateResolver

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

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
            self._initialize_from_template(
                template_name, dest, config, use_github=True, subdir=subdir
            )
        else:
            config = ProjectPrompter().ask_all()
            template_name = TemplateResolver.resolve(config)
            self._initialize_from_template(template_name, dest, config)

    def _initialize_from_template(
        self,
        template_name: str,
        dest: Path,
        config: dict | None = None,
        use_github: bool = False,
        subdir: str = "",
    ) -> None:
        """Clones and extracts the template into the destination directory."""
        config = config or {}
        orm = config.get("orm", "None")
        db_url = config.get("db_url")
        project_dir_name = dest.name if dest != Path(".") else None

        try:
            # Use spinner during initialization
            with console.status(
                "[yellow]nexy[/yellow] » "
                + t("init.initializing", "Initializing {name}...").format(name=template_name),
                spinner="dots",
            ):
                if use_github:
                    cloner = GitClone()
                    cloner.clone(cloner.repo, cloner.branch, dest, subdir=subdir)
                else:
                    local_src = _TEMPLATES_DIR / template_name
                    context = {
                        "orm": orm,
                        "db_url": db_url,
                        "project_type": config.get("project_type", "web"),
                        "FBRouter": config.get("FBRouter", False),
                        "client_framework": config.get("client_framework", "none"),
                    }
                    renderer = TemplateRenderer(local_src, dest, context)
                    renderer.render()

                    # Render shared files for each template type
                    shared_dir = _TEMPLATES_DIR / "_shared"
                    if template_name.startswith("web-"):
                        for sub_dir, rel_dest in [
                            ("web-components", "src/components"),
                            ("web", "."),
                        ]:
                            src = shared_dir / sub_dir
                            if src.is_dir():
                                tgt = dest / rel_dest if rel_dest != "." else dest
                                TemplateRenderer(src, tgt, context).render()

                        root_globale = dest / "globale.css"
                        if root_globale.exists():
                            (dest / "src").mkdir(parents=True, exist_ok=True)
                            shutil.move(str(root_globale), str(dest / "src" / "globale.css"))
                    elif template_name.startswith("api-"):
                        src = shared_dir / "api"
                        if src.is_dir():
                            TemplateRenderer(src, dest, context).render()

                    # Render configs/ for all template types
                    cfg_src = shared_dir / "configs"
                    if cfg_src.is_dir():
                        TemplateRenderer(cfg_src, dest / "src" / "configs", context).render()

                    # Render FBR-shared files for all *-fbr templates
                    if template_name.endswith("-fbr"):
                        fbr_src = shared_dir / "fbr"
                        if fbr_src.is_dir():
                            TemplateRenderer(fbr_src, dest / "src", context).render()

                    # Auto-generate empty __init__.py for Python packages
                    self._generate_init_files(dest / "src")

            # Auto-install dependencies
            installer = DependencyInstaller(dest, orm=orm)
            installer.install_all()

            # Generate __init__.py and .env post-init files
            self._generate_post_init_files(dest, orm, db_url)

            # Initialize migration tool if ORM chosen
            self._init_migration(orm, dest, db_url)

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

    def _generate_init_files(self, base: Path) -> None:
        """Auto-generate empty __init__.py in Python package dirs."""
        dirs_to_check = [base]
        dirs_to_check.extend(sorted(base.rglob("*")))
        for dir_path in dirs_to_check:
            if dir_path.is_dir() and not (dir_path / "__init__.py").exists():
                is_top_src = dir_path == base
                has_py = any(f.suffix == ".py" for f in dir_path.iterdir())
                has_nexy = any(f.suffix == ".nexy" for f in dir_path.iterdir())
                if is_top_src or has_py or has_nexy:
                    (dir_path / "__init__.py").write_text("")

    def _cleanup_build_artifacts(self, dest: Path) -> None:
        unwanted = ["build", "dist"]
        for folder_name in unwanted:
            folder_path = dest / folder_name
            if folder_path.exists() and folder_path.is_dir():
                shutil.rmtree(folder_path, ignore_errors=True)

    def _generate_post_init_files(self, dest: Path, orm: str, db_url: str | None) -> None:
        """Create __init__.py and .env files after template rendering."""
        if orm != "None":
            for model_dir in [
                dest / "src" / "models",
                dest / "src" / "apps",
                dest / "src" / "apps" / "users",
            ]:
                if model_dir.exists() and (model_dir / "user_model.py").exists():
                    (model_dir / "__init__.py").write_text("from .user_model import UserModel\n")
            for cfg_dir in [dest / "src" / "configs"]:
                if cfg_dir.exists():
                    (cfg_dir / "__init__.py").write_text("")

        # --- .env ---
        if db_url:
            env_file = dest / ".env"
            if not env_file.exists():
                env_file.write_text(f"DATABASE_URL={db_url}\n")

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

    def _init_migration(self, orm: str, dest: Path, db_url: str | None = None) -> None:
        if orm == "None":
            return
        tool: str | None = None
        if orm in ("SQLModel", "SQLAlchemy"):
            tool = "alembic"
        elif orm == "Tortoise-ORM":
            tool = "aerich"
        if not tool:
            return
        with console.status(
            f"[yellow]nexy[/yellow] » Initializing {tool}...",
            spinner="dots",
        ):
            if tool == "aerich":
                subprocess.run(
                    ["uv", "run", tool, "init", "-t", "src.configs.db.TORTOISE_ORM"],
                    cwd=dest,
                    capture_output=True,
                    shell=os.name == "nt",
                )
            else:
                subprocess.run(
                    ["uv", "run", tool, "init", tool],
                    cwd=dest,
                    capture_output=True,
                    shell=os.name == "nt",
                )
                # Render custom alembic env.py that wires up target_metadata
                alembic_dir = dest / "alembic"
                if alembic_dir.exists():
                    loader = FileSystemLoader(str(_TEMPLATES_DIR / "alembic"))
                    env = Environment(loader=loader)
                    env_path = alembic_dir / "env.py"
                    env_path.write_text(env.get_template("env.py.jinja2").render(orm=orm))
                    # Write DATABASE_URL into alembic.ini
                    if db_url:
                        self._write_alembic_ini_url(dest, db_url)

    @staticmethod
    def _write_alembic_ini_url(dest: Path, db_url: str) -> None:
        import re
        alembic_ini = dest / "alembic.ini"
        if not alembic_ini.exists():
            return
        content = alembic_ini.read_text(encoding="utf-8")
        content = re.sub(
            r"^sqlalchemy\.url\s*=.*",
            f"sqlalchemy.url = {db_url}",
            content,
            flags=re.MULTILINE,
        )
        alembic_ini.write_text(content, encoding="utf-8")

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
