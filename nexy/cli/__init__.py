
import typer
from typing import Optional

from nexy.cli.command import dev, start, build

CLI = typer.Typer(help="Nexy CLI - The Modular Meta-Framework")

@CLI.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Point d'entrée principal qui s'exécute si aucune commande n'est fournie."""
    if ctx.invoked_subcommand is None:
        typer.echo("NexyPy CLI - Utilisez --help pour voir les commandes disponibles.")


CLI.command()(dev)
CLI.command()(start)
CLI.command()(build)


__all__ = ["CLI"]
