from pathlib import Path

import typer

from nexy.i18n import t
from nexy.utils.common.console import console
from nexy.utils.init import InitProject


def init(
    arg_options: str | None = typer.Option(
        None,
        "--template",
        "-t",
        help="Initialize from a registered template (silent clone).",
    ),
) -> None:
    already = (
        Path("__nexy__").exists()
        or Path("nexyconfig.py").exists()
        or Path("vite.config.ts").exists()
    )
    if already:
        console.print("[red]nexy[/red] » " + t("init.already", "Project already initialized here"))
        raise typer.Exit(code=1)

    if arg_options is not None:
        InitProject().run(template=arg_options)
    else:
        InitProject().run()
