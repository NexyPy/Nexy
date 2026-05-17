import os
import time
from typing import Any, Callable, Optional
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from nexy.cli.commands.utilities.console import console
from nexy.compiler import Compiler
from nexy.core.config import Config

# Standard ANSI colors for simple logging
C = {
    "reset": "\033[0m",
    "dim": "\033[2m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
}

class WatchHandler(PatternMatchingEventHandler):
    def __init__(self, on_reload_api: Optional[Callable[[], None]] = None, min_interval: float = 0.5, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.on_reload_api = on_reload_api
        self._last_event_time: float = 0.0
        self._last_path: str = ""
        self._min_interval = min_interval
        self.compiler = Compiler()

    def _should_trigger(self, path: str) -> bool:
        current_time = time.time()
        if path == self._last_path and (current_time - self._last_event_time) < self._min_interval:
            return False
        self._last_event_time = current_time
        self._last_path = path
        return True

    def _normalize(self, p: str | bytes) -> str:
        return (p.decode() if isinstance(p, bytes) else p).replace("\\", "/").lstrip("./")


    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory:
            return
            
        path = self._normalize(event.src_path)
        
        if not self._should_trigger(path):
            return
            
        # Ignore system and dependency folders
        if path.startswith((".git/", "venv", ".venv/", "__nexy/", "__pycache__/", "node_modules/")):
            return

        needs_reload = False

        # 1. Compilation Logic
        if path.endswith((".nexy", ".mdx")):
            try:
                start_time = time.perf_counter()
                
                # Critical: Compile step execution
                self.compiler.compile(path)
                
                elapsed = time.perf_counter() - start_time
                timer = f"{elapsed:.2f}s"
                console.print(f"[green]nsc[/green] » [green]compile[/green] [dim]{path}[/dim] in [dim]{timer}[/dim] [green]✓[/green]")
                needs_reload = True
                
            except Exception as e:
                # Catching exceptions prevents the Observer thread from dying
                console.print(f"[red]nsc[/red] » [red]error[/red] while compiling [dim]{path}[/dim]")
                console.print(f"[red]│[/red] [bold]{type(e).__name__}:[/bold] {str(e)}")
                needs_reload = False
        
        # 2. Python files logic
        elif path.endswith(".py"):
            needs_reload = True
            if not path.startswith("__nexy__/"):
                print(f"{C['blue']}hmr{C['reset']} » {C['green']}update{C['reset']} {C['dim']}{path}{C['reset']} {C['green']}↺{C['reset']}")

        # 3. Trigger Uvicorn Reload
        if needs_reload and self.on_reload_api:
            try:
                self.on_reload_api()
            except Exception as e:
                console.print(f"[red]hmr[/red] » [red]error[/red] failed to reload server: {str(e)}")

    def on_any_event(self, event):
        path = self._normalize(event.src_path)
        if path.endswith((".nexy", ".mdx", ".py")):
            # Logic for cleaning up generated files can go here
            if self.on_reload_api:
                self.on_reload_api()
    def on_deleted(self, event: FileSystemEvent) -> None:
        path = self._normalize(event.src_path)
        if path.endswith((".nexy", ".mdx")):
            # Logic for cleaning up generated files can go here
            if self.on_reload_api:
                self.on_reload_api()

def create_observer(path: str, patterns: list[str], ignore_patterns: list[str], on_reload_api: Callable[[], None]):
    event_handler = WatchHandler(
        patterns=patterns,
        ignore_patterns=ignore_patterns,
        on_reload_api=on_reload_api,
        ignore_directories=True,
    )
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer