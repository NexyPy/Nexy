
import typer
from nexy.__version__ import __Version__
from nexy.cli.commands import dev, init, start, build
from nexy.cli.commands.utilities.console import console

version = __Version__().get()

CLI = typer.Typer(help="Nexy CLI - The Modular Meta-Framework")

@CLI.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Point d'entrée principal qui s'exécute si aucune commande n'est fournie."""
    if ctx.invoked_subcommand is None:
        console.print(version)
        typer.echo(" Utilisez nx/nexy --help pour voir les commandes disponibles.")


CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)
CLI.command()(init)


__all__ = ["CLI"]
