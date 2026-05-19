import shutil
import subprocess
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader

_TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"


def _detect_orm() -> tuple[str, str]:
    """Detect the active ORM.

    Returns (orm_name, tool).
    """
    cwd = Path.cwd()

    config_file = cwd / "nexyconfig.py"
    if config_file.exists():
        content = config_file.read_text()
        if "SQLModel" in content or "sqlmodel" in content:
            return ("SQLModel", "alembic")
        if "Tortoise" in content or "tortoise" in content:
            return ("Tortoise-ORM", "aerich")
        if "SQLAlchemy" in content or "sqlalchemy" in content:
            return ("SQLAlchemy", "alembic")

    try:
        import sqlmodel  # noqa: F401

        return ("SQLModel", "alembic")
    except ImportError:
        pass

    try:
        import tortoise  # noqa: F401

        return ("Tortoise-ORM", "aerich")
    except ImportError:
        pass

    try:
        import sqlalchemy  # noqa: F401

        return ("SQLAlchemy", "alembic")
    except ImportError:
        pass

    return ("", "")


def _run_tool(tool: str, args: list[str]) -> int:
    exe = shutil.which(tool)
    if not exe:
        typer.echo(f"Error: {tool} not found on PATH. Install it and try again.")
        raise typer.Exit(1)
    return subprocess.run([exe, *args], check=False).returncode


def _init_alembic(cwd: Path, orm_name: str) -> None:
    _run_tool("alembic", ["init", "alembic"])
    alembic_dir = cwd / "alembic"
    if alembic_dir.exists():
        loader = FileSystemLoader(str(_TEMPLATES_DIR / "alembic"))
        env = Environment(loader=loader)
        env_path = alembic_dir / "env.py"
        env_path.write_text(env.get_template("env.py.jinja2").render(orm=orm_name))
    _write_db_url_to_alembic_ini(cwd)


def _write_db_url_to_alembic_ini(cwd: Path) -> None:
    import os
    import re

    env_path = cwd / ".env"
    db_url = None
    if env_path.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except ImportError:
            pass
        db_url = os.getenv("DATABASE_URL")
    if not db_url:
        return
    alembic_ini = cwd / "alembic.ini"
    if not alembic_ini.exists():
        return
    content = alembic_ini.read_text(encoding="utf-8")
    content = re.sub(
        r"^sqlalchemy\.url\s*=.*",
        f"sqlalchemy.url = {db_url}",
        content,
        flags=re.MULTILINE,
    )
    alembic_ini.write_text(content, encoding="utf-8")


def _check_db_connection() -> None:
    import os

    env_path = Path.cwd() / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except ImportError:
            pass

    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        typer.echo("Error: DATABASE_URL not found in .env or environment.")
        raise typer.Exit(1)

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(db_url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
    except ImportError as e:
        typer.echo(f"Error: Missing database driver — {e}")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Error: Cannot connect to database — {e}")
        raise typer.Exit(1)


def migrate(
    message: str = typer.Option("", "--message", "-m", help="Migration message"),
    init: bool = typer.Option(False, "--init", help="Initialize migration tool"),
    upgrade: bool = typer.Option(False, "--upgrade", "-u", help="Apply pending migrations"),
) -> None:
    orm_name, tool = _detect_orm()
    cwd = Path.cwd()

    if not orm_name:
        typer.echo("No supported ORM found. Install one: sqlmodel, tortoise-orm, sqlalchemy")
        raise typer.Exit(1)

    typer.echo(f"-- {orm_name} ({tool}) --")

    if init:
        if tool == "alembic":
            _init_alembic(cwd, orm_name)
        elif tool == "aerich":
            _run_tool("aerich", ["init", "-t", "src.configs.db.TORTOISE_ORM"])
        return

    if tool == "alembic" and not (cwd / "alembic.ini").exists():
        typer.echo("Alembic not initialized. Run 'nx m --init' first.")
        raise typer.Exit(1)

    if tool == "aerich" and not (cwd / "aerich.ini").exists():
        typer.echo("Aerich not initialized. Run 'nx m --init' first.")
        raise typer.Exit(1)

    _check_db_connection()

    if upgrade:
        _run_tool(tool, ["upgrade", "head"])
        return

    args = ["revision", "--autogenerate"]
    if message:
        args += ["-m", message]
    _run_tool(tool, args)
