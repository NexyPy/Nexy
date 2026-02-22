import os
import time
from typing import Any, Callable, Optional
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from nexy.compiler import Compiler
from nexy.core.config import Config

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
    def __init__(self, on_reload_api: Optional[Callable] = None, min_interval: float = 0.5, **kwargs: Any) -> None:
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

    def _normalize(self, p: str) -> str:
        return (p.decode() if isinstance(p, bytes) else p).replace("\\", "/").lstrip("./")

    def on_modified(self, event: FileSystemEvent) -> None:
        if event.is_directory: return
        path = self._normalize(event.src_path)
        
        if not self._should_trigger(path): return
        if path.startswith((".git/", ".venv/", "__nexy__/", "__pycache__/", "node_modules/")): return

        needs_reload = False

        # 1. Compilation si nécessaire
        if path.endswith((".nexy", ".mdx")):
            print(f"{C['blue']}hmr{C['reset']} » {C['green']}update{C['reset']} {C['dim']}{path}{C['reset']} {C['green']}↺{C['reset']}")
            self.compiler.compile(path)
            needs_reload = True
        
        # 2. Si c'est un fichier Python, on doit reload aussi
        elif path.endswith(".py"):
            needs_reload = True
            print(f"{C['blue']}hmr{C['reset']} » {C['green']}update{C['reset']} {C['dim']}{path}{C['reset']} {C['green']}↺{C['reset']}")

        # 3. Déclenchement du redémarrage Uvicorn
        if needs_reload and self.on_reload_api:
            self.on_reload_api()

    def on_deleted(self, event: FileSystemEvent) -> None:
        # (Ta logique de suppression reste identique)
        path = self._normalize(event.src_path)
        if path.endswith((".nexy", ".mdx")):
            # Suppression des fichiers générés...
            if self.on_reload_api: self.on_reload_api()

def create_observer(path: str, patterns: list[str], ignore_patterns: list[str], on_reload_api: Callable) -> Observer:
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