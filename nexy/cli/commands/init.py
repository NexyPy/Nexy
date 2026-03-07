from typing import Optional
from pathlib import Path
import typer
from nexy.cli.commands.utilities.init_project import InitProject
from nexy.utils.console import console
from nexy.i18n import t


def init(
    template: Optional[str] = typer.Option(
        None,
        "--template",
        "-t",
        help="Initialize from a registered template (silent clone).",
    ),
    registry: Optional[str] = typer.Option(
        None,
        "--registry",
        help="Override template registry URL.",
    ),
) -> None:
    already = Path("__nexy__").exists() or Path("nexyconfig.py").exists() or Path("vite.config.ts").exists()
    if already:
        console.print("[red]nexy[/red] » " + t("init.already", "Project already initialized here"))
        raise typer.Exit(code=1)
    project = InitProject()
    if template or registry:
        project.apply_template(template_name=template, registry_url=registry)
    else:
        pass
