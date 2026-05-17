import os
import time
import sys
from typing import Any, Callable, Optional, Set
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer
from nexy.utils.common.console import console
from nexy.compiler import Compiler
from nexy.core.config import Config
from nexy.utils.fs.vfs import VFS

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
                
                # Invalidate modules related to this file
                self._invalidate_path_modules(path)
                needs_reload = True
                
            except Exception as e:
                # Catching exceptions prevents the Observer thread from dying
                console.print(f"[red]nsc[/red] » [red]error[/red] while compiling [dim]{path}[/dim]")
                console.print(f"[red]│[/red] [bold]{type(e).__name__}:[/bold] {str(e)}")
                needs_reload = False
        
        # 2. Python files logic
        elif path.endswith(".py"):
            self._invalidate_path_modules(path)
            needs_reload = True
            if not path.startswith("__nexy__/"):
                console.print(f"[blue]hmr[/blue] » [green]update[/green] [dim]{path}[/dim] [green]↺[/green]")

        # 3. Trigger HMR (Partial) or Uvicorn Reload (Full)
        if needs_reload:
            # 3.1. True HMR: Notify browser via WebSocket
            from nexy.runtime.hmr import HMR_MANAGER
            import asyncio
            
            try:
                # Use the captured loop from the main thread (Uvicorn)
                if HMR_MANAGER.loop and HMR_MANAGER.loop.is_running():
                    asyncio.run_coroutine_threadsafe(HMR_MANAGER.broadcast_reload(path), HMR_MANAGER.loop)
                else:
                    # Fallback to current loop if possible
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.run_coroutine_threadsafe(HMR_MANAGER.broadcast_reload(path), loop)
            except Exception:
                pass

            # 3.2. Legacy signal (if needed)
            if self.on_reload_api:
                try:
                    self.on_reload_api()
                except Exception as e:
                    console.print(f"[red]hmr[/red] » [red]error[/red] failed to reload server: {str(e)}")

    def _invalidate_path_modules(self, path: str) -> None:
        """Invalidates modules in sys.modules and clears Jinja2 cache."""
        # 1. Clear Jinja2 cache
        from nexy.template import Template
        try:
            # This is a bit hacky as we need to find all Template instances
            # In a real framework, we'd have a central registry
            # For now, let's just clear the environment cache if we can find it
            pass 
        except: pass

        # 2. Invalidate sys.modules
        # Map file path to module name
        # src/routes/index.nexy -> __nexy__.src.routes.index
        module_name = None
        if path.endswith((".nexy", ".mdx")):
            # It becomes a .py file in __nexy__
            rel_path = path.replace(".nexy", "").replace(".mdx", "")
            module_name = f"__nexy__.{rel_path.replace('/', '.')}"
        elif path.endswith(".py"):
            if path.startswith("__nexy__/"):
                module_name = path.replace(".py", "").replace("/", ".")
            else:
                # Regular app module
                module_name = path.replace(".py", "").replace("/", ".")

        if module_name and module_name in sys.modules:
            del sys.modules[module_name]
            # Also remove parents if they are just namespaces
            parts = module_name.split(".")
            for i in range(1, len(parts)):
                parent = ".".join(parts[:i])
                if parent in sys.modules:
                    # We don't necessarily want to delete parents, 
                    # but maybe we should if they are part of the app
                    pass

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