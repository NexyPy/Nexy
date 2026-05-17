import sys
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.cli.commands.utilities.console import console
from nexy.cli.commands.utilities.server import Server
from nexy.core.config import Config
from nexy.frontend import FrontendGenerator
from nexy.i18n import t


def build() -> None:
    config = Config()
    version = __Version__().get()
    Server.check_nexy_prod()
    console.print(f"nexy@{version} build")
    with console.status("\n[green]nsc[/green] » compile...", spinner="dots"):
        FrontendGenerator().generate(ssg=True)
        Builder().build(showlog=True)
    
    if getattr(config, "useVite", False):
        try :
            vite_proc = Server.vite(build=True)
            vite_proc.wait()
        except Exception as e:
            console.print(t("build.vite_failed", f"Vite build failed. {e}").format(error=e))
            sys.exit(1)
