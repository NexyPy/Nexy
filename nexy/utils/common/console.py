from typing import Any

from rich.console import Console as RichConsole

console: RichConsole = RichConsole()


def _safe_print(*args: Any, **kwargs: Any) -> None:
    console.print(*args, **kwargs)
