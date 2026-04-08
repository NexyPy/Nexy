
import typer
from nexy.__version__ import __Version__
from nexy.cli.commands import dev, init, start, build
from nexy.utils.console import console
from nexy.i18n import t

VERSION = __Version__().get()

CLI = typer.Typer(help=t("cli.help", "Nexy CLI"))



@CLI.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version")
    ) -> None:
    """Main entry point executed when no command is provided."""

    if version:
        console.print(f"[green]nexy[/green] {VERSION}")
        raise typer.Exit()
    
    if ctx.invoked_subcommand is None:
        console.print(VERSION)
        typer.echo(f" {t('cli.no_command', 'Use nx/nexy --help to see commands.')}")

CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)
CLI.command()(init)


__all__ = ["CLI"]
