from __future__ import annotations
import shutil
from pathlib import Path
from nexy.__version__ import __Version__
from nexy.cli.commands.utilities.console import console
from nexy.i18n import t
from .clone import GitClone
from .prompts import ProjectPrompter
from .resolver import TemplateResolver
from .dependencies import DependencyInstaller

class InitProject:
    """Orchestrates the project initialization process."""

    def __init__(self) -> None:
        self.version = __Version__().get()

    def run(self, template: str | None = None) -> None:
        """Main execution flow for project initialization."""
        console.print(t("init.title", "nexy init").format(version=self.version))

        if template:
            subdir = f"templates/{template}"
            template_name = template
        else:
            config = ProjectPrompter().ask_all()
            subdir = TemplateResolver.resolve(config)
            # Extract a cleaner name from the subdir (e.g. templates/web-fbr-react -> web-fbr-react)
            template_name = subdir.replace("templates/", "")

        self._initialize_from_template(subdir, template_name)

    def _initialize_from_template(self, subdir: str, template_name: str) -> None:
        """Clones and extracts the template into the current directory."""
        dest = Path(".")
        cloner = GitClone()
        
        try:
            # Use spinner during initialization
            with console.status(f"[yellow]nexy[/yellow] » " + t("init.initializing", "Initializing {name}...").format(name=template_name), spinner="dots"):
                cloner.clone(cloner.repo, cloner.branch, dest, subdir=subdir)
            
            # Auto-install dependencies
            installer = DependencyInstaller(dest)
            installer.install_all()
            
            # Final cleanup of unwanted folders
            self._cleanup_unwanted_folders(dest)
            
            self._print_success_message()
        except Exception as e:
            console.print(f"\n[red]nexy[/red] » " + t("init.error", "Initialization failed: {error}").format(error=str(e)))
            raise

    def _cleanup_unwanted_folders(self, dest: Path) -> None:
        """Removes folders like build, dist, or egg-info that might have been created."""
        unwanted = ["build", "dist"]
        for folder_name in unwanted:
            folder_path = dest / folder_name
            if folder_path.exists() and folder_path.is_dir():
                shutil.rmtree(folder_path, ignore_errors=True)
        
        # Also clean up egg-info files for python
        for item in dest.glob("*.egg-info"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)

    def _print_success_message(self) -> None:
        """Prints a detailed success message with next steps."""
        console.print(f"\n[green]nexy[/green] » " + t("init.success_title", "Project initialized successfully!"))
        console.print("\n" + t("init.next_steps", "Next steps:"))
        
        console.print(f"  1. [cyan]nexy dev[/cyan] - " + t("init.step_run_dev", "Start the development server"))
        console.print(f"  2. [cyan]nexy --help[/cyan] - " + t("init.step_help", "Explore available commands"))
        
        console.print("\n" + t("init.happy_coding", "Happy coding with Nexy!"))
