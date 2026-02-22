from typing import Optional
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server
from nexy.cli.commands.utilities.watcher import create_observer
from nexy.cli.commands.utilities.console import Console

def dev(port: Optional[int] = None, host: Optional[str] = None) -> None:
    path = "."
    config = Config()
    extensions = config.WATCH_EXTENSIONS_GLOB
    exclusions = config.WATCH_EXCLUDE_PATTERNS
    extra_exclusions = getattr(config, "excludeDirs", [])
    exclusions.extend([f"*/{name}/*" for name in extra_exclusions])

    version = __Version__().get()
    Console.banner(f"nexy@{version} dev")

    Console.info("ŋ compile...")
    Builder().build()

    observer = create_observer(path, extensions, exclusions)
    try:
        vite_proc = None
        if getattr(config, "useVite", False):
            try:
                vite_proc = Server.vite_async()
                Console.success("Vite dev server started")
            except Exception:
                vite_proc = None
                Console.error("Failed to start Vite dev server")

        run_host = host if host is not None else getattr(config, "useHost", "0.0.0.0")
        run_port = Server.resolve_port(run_host, port)

    finally:
        Console.info(f"Uvicorn: http://{run_host}:{run_port} (reload)")
        try:
            Server.uvicorn(host=run_host, port=run_port, reload=True)
        except (KeyboardInterrupt, SystemExit):
            Console.warn("ŋ dev server stopped")
        observer.stop()
        observer.join()
        if vite_proc is not None:
            try:
                vite_proc.terminate()
                vite_proc.wait(timeout=5)
            except Exception:
                pass
        Console.success("Watcher stopped.")
