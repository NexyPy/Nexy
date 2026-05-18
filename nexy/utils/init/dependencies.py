import os
import shutil
import subprocess
import sys
from pathlib import Path

from nexy.i18n import t
from nexy.utils.common.console import console

_ORM_PACKAGES: dict[str, str] = {
    "SQLModel": "sqlmodel",
    "SQLAlchemy": "sqlalchemy",
    "Tortoise-ORM": "tortoise-orm",
}


class DependencyInstaller:
    """Handles automatic installation of dependencies for different project types."""

    def __init__(self, directory: Path = Path("."), orm: str | None = None):
        self.directory = directory
        self.orm = orm
        self.is_windows = os.name == "nt"
        self.venv_dir = directory / ".venv"

    # -- helpers ----------------------------------------------------------------

    def _python(self) -> str:
        if self.is_windows:
            return str(self.venv_dir / "Scripts" / "python.exe")
        return str(self.venv_dir / "bin" / "python")

    def _run(self, cmd: list[str], desc: str) -> bool:
        try:
            subprocess.run(
                cmd,
                cwd=self.directory,
                check=True,
                capture_output=True,
                shell=self.is_windows,
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[red]nexy[/red] » {desc} failed")
            output = (e.stdout or b"") + (e.stderr or b"")
            if output:
                console.print(output.decode("utf-8", errors="replace")[:500])
            return False

    # -- public API ------------------------------------------------------------

    def install_all(self) -> None:
        self._install_uv()
        self.create_venv()
        self.install_node_dependencies()
        self.install_python_dependencies()
        self.install_orm()
        self._remove_egg_info()

    def _install_uv(self) -> None:
        if shutil.which("uv") is not None:
            return
        with console.status(
            "[yellow]nexy[/yellow] » Installing uv...",
            spinner="dots",
        ):
            self._run(
                [sys.executable, "-m", "pip", "install", "uv"],
                "uv installation",
            )

    def create_venv(self) -> None:
        if self.venv_dir.exists():
            return

        with console.status(
            "[yellow]nexy[/yellow] » Creating virtual environment...",
            spinner="dots",
        ):
            self._run(["uv", "venv", str(self.venv_dir)], "Virtual environment creation")

    def install_node_dependencies(self) -> None:
        package_json = self.directory / "package.json"
        vite_config = self.directory / "vite.config.ts"
        pnpm_lock = self.directory / "pnpm-lock.yaml"
        yarn_lock = self.directory / "yarn.lock"

        if package_json.exists() and vite_config.exists():
            if pnpm_lock.exists() and shutil.which("pnpm"):
                cmd = ["pnpm", "install"]
            elif yarn_lock.exists() and shutil.which("yarn"):
                cmd = ["yarn", "install"]
            elif shutil.which("npm"):
                cmd = ["npm", "install"]
            else:
                console.print(
                    "[yellow]nexy[/yellow] » "
                    + t(
                        "init.node_manager_not_found",
                        "No Node.js package manager found. Install deps manually.",
                    )
                )
                return

            with console.status(
                "[yellow]nexy[/yellow] » "
                + t("init.installing_node", "Installing Node.js dependencies..."),
                spinner="dots",
            ):
                self._run(cmd, "Node.js dependencies installation")
                console.print(
                    "[green]nexy[/green] » "
                    + t("init.node_installed", "Node.js dependencies installed.")
                )

    def install_python_dependencies(self) -> None:
        pyproject = self.directory / "pyproject.toml"
        if not pyproject.exists():
            return

        with console.status(
            "[yellow]nexy[/yellow] » "
            + t("init.installing_python", "Installing Python dependencies..."),
            spinner="dots",
        ):
            self._run(["uv", "sync"], "Python dependencies installation")

    def install_orm(self) -> None:
        if not self.orm or self.orm == "None":
            return
        package = _ORM_PACKAGES.get(self.orm)
        if not package:
            return
        with console.status(
            f"[yellow]nexy[/yellow] » Installing {self.orm}...",
            spinner="dots",
        ):
            self._run(["uv", "add", package], f"{self.orm} installation")

    def _remove_egg_info(self) -> None:
        for item in self.directory.glob("**/*.egg-info"):
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
