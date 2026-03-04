import sys
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.cli.commands.utilities.console import console
from nexy.cli.commands.utilities.server import Server
from nexy.core.config import Config


def build():
    config = Config()
    version = __Version__().get()
    console.print(f"nexy@{version} build")
    with console.status("\n[green]nsc[/green] » compile...", spinner="dots"):
        Builder().build(showlog=True)
    
    if getattr(config, "useVite", False):
        try :
            vite_proc = Server.vite(build=True)
            vite_proc.wait()
        except Exception as e:
            console.print(f"x Erreur : Le build Vite a échoué. {e}")
            sys.exit(1)
