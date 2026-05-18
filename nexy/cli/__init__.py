import contextlib
import functools
import sys

import typer
import typer.rich_utils

from nexy.__version__ import __Version__
from nexy.cli.commands import build, dev, init, start
from nexy.cli.commands.migrate import migrate
from nexy.cli.commands.new import new
from nexy.i18n import t
from nexy.utils.common.console import console

# Ensure UTF-8 encoding for stdout/stderr so Rich can render Unicode box-drawing characters
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    with contextlib.suppress(Exception):
        sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    with contextlib.suppress(Exception):
        sys.stderr.reconfigure(encoding="utf-8")

# Force rounded Unicode box-drawing characters in Typer's Rich help output
_orig_get_console = typer.rich_utils._get_rich_console


@functools.wraps(_orig_get_console)
def _nexy_get_console(stderr: bool = False):
    c = _orig_get_console(stderr=stderr)
    c.safe_box = False
    return c


typer.rich_utils._get_rich_console = _nexy_get_console

VERSION = __Version__().get()

CLI = typer.Typer(
    help=t("cli.help", "Nexy CLI"),
    context_settings={"help_option_names": ["-h", "--help"]},
)


@CLI.callback(invoke_without_command=True)
def main(
    ctx: typer.Context, version: bool = typer.Option(False, "--version", "-v", help="Show version")
) -> None:
    """Main entry point executed when no command is provided."""

    if version:
        console.print(f"[green]nexy[/green] {VERSION}")
        raise typer.Exit()
    if ctx.invoked_subcommand is None:
        # Build polished welcome banner with brand identity and clear next steps
        console.print()
        console.print(f"[bold green]nexy[/bold green] [dim]{VERSION}[/dim]")
        console.print()
        console.print("[italic]The modern full-stack framework that just works[/italic]")
        console.print()
        console.print("[bold cyan]Available Commands:[/bold cyan]")
        # Format core commands with aligned descriptions for professional readability
        commands = [
            ("new [dim]<project-name>[/dim]", "Create a new project in a new directory"),
            ("init", "Initialize Nexy in the current directory"),
            ("dev", "Start local development server with hot reload"),
            ("start", "Start production server"),
            ("build", "Compile project for production deployment"),
            ("migrate", "Run ORM migrations (auto-detects ORM)"),
        ]
        # Calculate max command length for perfect alignment
        max_cmd_len = max(len(cmd) for cmd, _ in commands)
        for cmd, desc in commands:
            console.print(f"  [yellow]{cmd.ljust(max_cmd_len)}[/yellow]  {desc}")
        console.print()
        console.print("[dim]Run [bold]nx or nexy <command> --help[/bold] for detailed usage[/dim]")
        console.print()


CLI.command()(dev)
CLI.command(name="d", hidden=True)(dev)
CLI.command()(start)
CLI.command(name="s", hidden=True)(start)
CLI.command()(build)
CLI.command(name="b", hidden=True)(build)
CLI.command()(init)
CLI.command(name="i", hidden=True)(init)
CLI.command()(new)
CLI.command(name="n", hidden=True)(new)
CLI.command()(migrate)
CLI.command(name="m", hidden=True)(migrate)
# CLI.command(name="a", hidden=True)(add)
# CLI.command()(add)


__all__ = ["CLI"]
