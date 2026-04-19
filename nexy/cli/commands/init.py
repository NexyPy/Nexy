from typing import Optional
from pathlib import Path
import typer
from nexy.cli.commands.utilities.init import InitProject
from nexy.utils.console import console
from nexy.i18n import t


def init(
    arg_options: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Initialize from a registered template (silent clone).",
    )
) -> None: 
    already = Path("__nexy__").exists() or Path("nexyconfig.py").exists() or Path("vite.config.ts").exists()
    if already:
        console.print("[red]nexy[/red] » " + t("init.already", "Project already initialized here"))
        raise typer.Exit(code=1)
    
    if not arg_options is None:
        InitProject().run(template=arg_options)
    else:
        InitProject().run()
