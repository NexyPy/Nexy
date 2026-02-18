import os
import time
from typing import Any, Optional

import uvicorn
from watchdog.events import FileSystemEvent, PatternMatchingEventHandler
from watchdog.observers import Observer

from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.compiler import Compiler
from nexy.core.config import Config


class MonHandler(PatternMatchingEventHandler):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.last_event_time: float = 0.0
        self.last_path: str = ""
        self.compiler = Compiler()

    def should_trigger(self, path: str) -> bool:
        current_time = time.time()
        if path == self.last_path and (current_time - self.last_event_time) < 0.1:
            return False

        self.last_event_time = current_time
        self.last_path = path
        return True
    def _compile(self, path: str) -> None:
            print(f"ŋ compile : {path}")
            self.compiler.compile(path)


    def on_modified(self, event: FileSystemEvent) -> None:
        raw_path = event.src_path
        path = raw_path.decode() if isinstance(raw_path, bytes) else raw_path
        if self.should_trigger(path):
            npath = path.replace("\\", "/").lstrip("./")

            if npath.startswith(
                (
                    ".git/",
                    ".venv/",
                    "__nexy__/",
                    "__pycache__/",
                    "venv/",
                    "node_modules/",
                )
            ):
                return
            
            print(f"File : '{npath}' is updated")
            if npath.endswith(".nexy") or npath.endswith(".mdx"):
                self._compile(npath)

    def on_deleted(self, event: FileSystemEvent) -> None:
        raw_path = event.src_path
        path = raw_path.decode() if isinstance(raw_path, bytes) else raw_path
        if self.should_trigger(path):
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


def dev(port: Optional[int] = None) -> None:
    path = "."
    extensions = ["*.py", "*.mdx", "*.nexy"]
    exclusions = [
        "*/.git/*",
        "*./.venv/*",
        "*./__nexy__/*",
        "*/__pycache__/*",
        "*/venv/*",
        "*/.venv/*",
        "*/__nexy__/*",
        "*/node_modules/*",
        "*.tmp",
    ]

    config = Config()
    extra_exclusions = getattr(config, "excludeDirs", [])
    exclusions.extend(extra_exclusions)

    version = __Version__().get()
    print(f"> nexy@{version} dev")

    print("ŋ compile...")
    Builder().build()

    event_handler = MonHandler(
        patterns=extensions,
        ignore_patterns=exclusions,
        ignore_directories=True,
    )

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    host = getattr(config, "useHost", "0.0.0.0")
    default_port = getattr(config, "usePort", 8000)
    run_port = port if port is not None else default_port

    

    try:
        uvicorn.run(
            "nexy.server.app:_server",
            host=host,
            port=run_port,
            reload=True,
        
        )
        # while True:
            # time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        
        print("ŋ dev server stopped")
    finally:
        observer.stop()
        observer.join()
        print("Watcher stopped.")
