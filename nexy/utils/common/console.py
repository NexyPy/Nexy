from rich.console import Console as RichConsole
from typing import Any

console: RichConsole = RichConsole()

def _safe_print(*args: Any, **kwargs: Any) -> None:
    console.print(*args, **kwargs)

