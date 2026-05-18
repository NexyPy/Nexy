import subprocess
import sys
from pathlib import Path

import typer


def _detect_orm() -> tuple[str, str, str]:
    cwd = Path.cwd()

    try:
        import sqlmodel  # noqa: F401

        has_alembic = (cwd / "alembic.ini").exists()
        return (
            "SQLModel",
            "alembic",
            "alembic revision --autogenerate" if has_alembic else "alembic init alembic",
        )
    except ImportError:
        pass

    try:
        import tortoise  # noqa: F401

        has_aerich = (cwd / "aerich.ini").exists()
        if has_aerich:
            return ("Tortoise-ORM", "aerich", "aerich migrate")
        return ("Tortoise-ORM", "aerich", "aerich init -t config.TORTOISE_ORM")
    except ImportError:
        pass

    try:
        import sqlalchemy  # noqa: F401

        has_alembic = (cwd / "alembic.ini").exists()
        return (
            "SQLAlchemy",
            "alembic",
            "alembic revision --autogenerate" if has_alembic else "alembic init alembic",
        )
    except ImportError:
        pass

    return ("", "", "")


def migrate(
    message: str = typer.Option("", "--message", "-m", help="Migration message"),
    init: bool = typer.Option(False, "--init", help="Initialize migration tool"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Apply pending migrations"),
) -> None:
    orm_name, tool, _init_tool = _detect_orm()

    if not orm_name:
        typer.echo("No supported ORM found. Install one: sqlmodel, tortoise-orm, sqlalchemy")
        raise typer.Exit(1)

    typer.echo(f"-- {orm_name} ({tool}) --")

    if init:
        subprocess.run([sys.executable, "-m", tool, "init", "alembic"], check=False)
        return

    if upgrade:
        subprocess.run([sys.executable, "-m", tool, "upgrade", "head"], check=False)
        return

    msg = f' -m "{message}"' if message else ""
    subprocess.run(
        f"{sys.executable} -m {tool} revision --autogenerate{msg}",
        shell=True,
        check=False,
    )
