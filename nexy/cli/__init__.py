
import typer
from typing import Optional

from nexy.cli.commands import dev, init, start, build

CLI = typer.Typer(help="Nexy CLI - The Modular Meta-Framework")

@CLI.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Point d'entrée principal qui s'exécute si aucune commande n'est fournie."""
    if ctx.invoked_subcommand is None:
        typer.echo(" Utilisez nx --help pour voir les commandes disponibles.")


CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)
CLI.command()(init)


__all__ = ["CLI"]
