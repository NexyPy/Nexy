import subprocess
import sys
import time

from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.frontend import FrontendGenerator
from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.server.server import Server


def build(check: bool = False) -> None:
    build_start = time.perf_counter()
    config = Config()
    version = __Version__().get()
    Server.check_nexy_prod()
    console.print(f"nexy@{version} build")
    with console.status("\n[green]nsc[/green] » compile...", spinner="dots"):
        FrontendGenerator().generate(ssg=True)
        Builder().build(showlog=True)
        from nexy.utils.fs.vfs import VFS

        VFS().flush_to_disk()

    if config.useVite:
        try:
            vite_proc = Server.vite(build=True)
            vite_proc.wait()
        except Exception as e:
            console.print(t("build.vite_failed", f"Vite build failed. {e}").format(error=e))
            sys.exit(1)

    if check:
        _run_checks()

    build_elapsed = time.perf_counter() - build_start
    build_timer = f"{build_elapsed:.2f}s"
    console.print(
        "\n[green]nsc[/green] » [green]build[/green]"
        f" in [reset][dim]{build_timer}[/dim] [green]✓[/green]"
    )


def _run_checks() -> None:
    console.print("\n[bold]Running quality checks...[/bold]\n")
    checks = [
        ("ruff check", ["ruff", "check", "."]),
        ("ruff format", ["ruff", "format", ".", "--check"]),
        ("mypy", [sys.executable, "-m", "mypy", "."]),
    ]
    failed = False
    for name, cmd in checks:
        with console.status(f"[cyan]{name}[/cyan]..."):
            r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0:
            console.print(f"  [green]✓[/green] {name}")
        else:
            console.print(f"  [red]✘[/red] {name}")
            if r.stdout:
                console.print(r.stdout)
            if r.stderr:
                console.print(f"[red]{r.stderr}[/red]")
            failed = True
    if failed:
        console.print("\n[red]Quality checks failed.[/red]")
        sys.exit(1)
    console.print("\n[green]All quality checks passed.[/green]")
