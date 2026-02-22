from typing import Optional
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server
from nexy.cli.commands.utilities.watcher import create_observer
from nexy.cli.commands.utilities.console import Console
from nexy.utils.ports import generate_port


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

    run_host = host if host is not None else getattr(config, "useHost", "0.0.0.0")
    base_port = port if port is not None else getattr(config, "usePort", 3000)
    server_port, client_port = generate_port(run_host, base_port)

    observer = create_observer(path, extensions, exclusions)
    vite_proc = None

    try:
        if getattr(config, "useVite", False):
            vite_proc = Server.vite(port=client_port)
            Console.success("Vite dev server started")
    except Exception:
        Console.error("Failed to start watcher")
    try:
        Server.uvicorn(host=run_host, port=server_port, reload=True)
    except (KeyboardInterrupt, SystemExit):
        Console.warn("ŋ dev server stopped")
    finally:
        observer.stop()
        observer.join()
        if vite_proc is not None:
            try:
                vite_proc.terminate()
                vite_proc.wait(timeout=5)
            except Exception:
                pass
        Console.success("Watcher stopped.")
