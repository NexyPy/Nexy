from __future__ import annotations
from pathlib import Path
from nexy.__version__ import __Version__
from nexy.cli.commands.utilities.console import console
from nexy.i18n import t
from .clone import GitClone
from .prompts import ProjectPrompter
from .resolver import TemplateResolver

class InitProject:
    """Orchestrates the project initialization process."""

    def __init__(self) -> None:
        self.version = __Version__().get()

    def run(self, template: str | None = None) -> None:
        """Main execution flow for project initialization."""
        console.print(t("init.title", "nexy init").format(version=self.version))

        if template:
            subdir = f"templates/{template}"
        else:
            config = ProjectPrompter().ask_all()
            subdir = TemplateResolver.resolve(config)

        self._initialize_from_template(subdir)

    def _initialize_from_template(self, subdir: str) -> None:
        """Clones and extracts the template into the current directory."""
        dest = Path(".")
        cloner = GitClone()
        
        try:
            cloner.clone(cloner.repo, cloner.branch, dest, subdir=subdir)
            console.print(f"\n[green]nexy[/green] » " + t("init.success", "Project initialized successfully!"))
        except Exception as e:
            console.print(f"\n[red]nexy[/red] » " + t("init.error", "Initialization failed: {error}").format(error=str(e)))
            raise
