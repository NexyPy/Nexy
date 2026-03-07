
import typer
from nexy.__version__ import __Version__
from nexy.cli.commands import dev, init, start, build
from nexy.utils.console import console
from nexy.i18n import t

version = __Version__().get()

CLI = typer.Typer(help=t("cli.help", "Nexy CLI"))

@CLI.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Main entry point executed when no command is provided."""
    if ctx.invoked_subcommand is None:
        console.print(version)
        typer.echo(f" {t('cli.no_command', 'Use nx/nexy --help to see commands.')}")


CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)
CLI.command()(init)


__all__ = ["CLI"]
