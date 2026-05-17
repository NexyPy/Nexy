import typer

from nexy.__version__ import __Version__
from nexy.cli.commands import add, build, dev, init, start
from nexy.i18n import t
from nexy.utils.common.console import console

VERSION = __Version__().get()

CLI = typer.Typer(help=t("cli.help", "Nexy CLI"))


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
            ("init [dim]<project-name>[/dim]", "Initialize a new Nexy project"),
            ("dev", "Start local development server with hot reload"),
            ("start", "Start production server"),
            ("build", "Compile project for production deployment"),
            # ("add <package>", "Install and integrate a new package")
        ]
        # Calculate max command length for perfect alignment
        max_cmd_len = max(len(cmd) for cmd, _ in commands)
        for cmd, desc in commands:
            console.print(f"  [yellow]{cmd.ljust(max_cmd_len)}[/yellow]  {desc}")
        console.print()
        console.print(
            "[dim]Run [bold]nx or nexy <command> --help[/bold] for detailed usage of any command[/dim]"
        )
        console.print()


CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)
CLI.command()(init)
# CLI.command()(add)


__all__ = ["CLI"]
