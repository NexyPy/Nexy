import sys
from pathlib import Path

import typer

from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.init import InitProject


def init() -> None:
    if (
        Path("__nexy__").exists()
        or Path("nexyconfig.py").exists()
        or Path("vite.config.ts").exists()
    ):
        console.print("[red]nexy[/red] » " + t("init.already", "Project already initialized here"))
        raise typer.Exit(code=1)

    try:
        InitProject().run()
    except KeyboardInterrupt:
        print()
        sys.exit(130)
