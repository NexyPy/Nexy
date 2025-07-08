"""
Author: Espoir Loémba

This module provides functionality for building Nexy projects via the command line interface.
"""

import subprocess
import logging
from os import path, environ
from sys import platform
from typer import Option, Argument
from nexy.cli.core.constants import Console, CMD
from nexy.cli.core.utils import print_banner


@CMD.command()
def build():
    """Builds the Nexy project."""        
    logging.info("Building the project...")
    subprocess.run(["npm ","run","build","--watch"], check=True)
    Console.print(f"[green]Build completed successfully![/green]")
    
