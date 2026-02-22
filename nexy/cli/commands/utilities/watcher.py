import os
import time
from typing import Any
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from nexy.compiler import Compiler
from nexy.core.config import Config

class WatchHandler(PatternMatchingEventHandler):
    def __init__(self, min_interval: float = 0.1, **kwargs: Any) -> None:
        super().__init__(**kwargs)
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

    def _compile(self, path: str) -> None:
        print(f"ŋ compile : {path}")
        self.compiler.compile(path)

    def on_modified(self, event: FileSystemEvent) -> None:
        path = self._normalize(event.src_path)
        if not self._should_trigger(path):
            return
        if path.startswith((".git/", ".venv/", "__nexy__/", "__pycache__/", "venv/", "node_modules/")):
            return
        print(f"File : '{path}' is updated")
        if path.endswith((".nexy", ".mdx")):
            self._compile(path)

    def on_deleted(self, event: FileSystemEvent) -> None:
        path = self._normalize(event.src_path)
        if not self._should_trigger(path):
            return
        compiled_path = path
        template_path = path
        if path.endswith(".nexy"):
            compiled_path = Config.NAMESPACE + path.replace(".nexy", ".py")
            template_path = Config.NAMESPACE + path.replace(".nexy", ".html")
        elif path.endswith(".mdx"):
            compiled_path = Config.NAMESPACE + path.replace(".mdx", ".py")
            template_path = Config.NAMESPACE + path.replace(".mdx", ".md")
        if os.path.exists(compiled_path) and path.endswith((".nexy", ".mdx")):
            os.remove(compiled_path)
            os.remove(template_path)
            print(f"File : '{path}' is deleted")

def create_observer(path: str, patterns: list[str], ignore_patterns: list[str], ignore_directories: bool = True) -> Observer:
    event_handler = WatchHandler(
        patterns=patterns,
        ignore_patterns=ignore_patterns,
        ignore_directories=ignore_directories,
    )
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer
