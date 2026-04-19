import shutil
import subprocess
import os
from pathlib import Path
from nexy.cli.commands.utilities.console import console
from nexy.i18n import t

class DependencyInstaller:
    """Handles automatic installation of dependencies for different project types."""

    def __init__(self, directory: Path = Path(".")):
        self.directory = directory
        self.is_windows = os.name == "nt"

    def install_all(self) -> None:
        """Checks for dependency files and runs installers if found."""
        self.install_node_dependencies()
        self.install_python_dependencies()

    def install_node_dependencies(self) -> None:
        """Installs Node.js packages if package.json and vite.config.ts are present."""
        package_json = self.directory / "package.json"
        vite_config = self.directory / "vite.config.ts"
        pnpm_lock = self.directory / "pnpm-lock.yaml"
        yarn_lock = self.directory / "yarn.lock"

        if package_json.exists() and vite_config.exists():
            # Determine which package manager to use
            if pnpm_lock.exists() and shutil.which("pnpm"):
                cmd = ["pnpm", "install"]
            elif yarn_lock.exists() and shutil.which("yarn"):
                cmd = ["yarn", "install"]
            elif shutil.which("npm"):
                cmd = ["npm", "install"]
            else:
                console.print(f"[yellow]nexy[/yellow] » " + t("init.node_manager_not_found", "No Node.js package manager found (npm, pnpm, yarn). Please install dependencies manually."))
                return

            with console.status("[yellow]nexy[/yellow] » " + t("init.installing_node", "Installing Node.js dependencies..."), spinner="dots"):
                try:
                    subprocess.run(
                        cmd, 
                        cwd=self.directory, 
                        check=True, 
                        capture_output=True,
                        shell=self.is_windows
                    )
                    console.print(f"[green]nexy[/green] » " + t("init.node_installed", "Node.js dependencies installed."))
                except subprocess.CalledProcessError:
                    console.print(f"[red]nexy[/red] » " + t("init.node_install_failed", "Failed to install Node.js dependencies. Please run '{cmd}' manually.").format(cmd=" ".join(cmd)))

    def install_python_dependencies(self) -> None:
        """Installs Python dependencies if pyproject.toml is present."""
        pyproject = self.directory / "pyproject.toml"

        if pyproject.exists():
            with console.status("[yellow]nexy[/yellow] » " + t("init.installing_python", "Installing Python dependencies..."), spinner="dots"):
                try:
                    subprocess.run(
                        ["pip", "install", "."], 
                        cwd=self.directory, 
                        check=True, 
                        capture_output=True,
                        shell=self.is_windows
                    )
                    console.print(f"[green]nexy[/green] » " + t("init.python_installed", "Python dependencies installed."))
                except subprocess.CalledProcessError:
                    console.print(f"[red]nexy[/red] » " + t("init.python_install_failed", "Failed to install Python dependencies. Please install them manually."))
