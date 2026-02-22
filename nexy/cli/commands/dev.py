import time
from typing import Optional
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server
from nexy.cli.commands.utilities.watcher import create_observer
from nexy.cli.commands.utilities.console import Console
from nexy.utils.ports import generate_port

def dev(port: Optional[int] = None, host: Optional[str] = None) -> None:
    config = Config()
    version = __Version__().get()
    Console.banner(f"nexy@{version} dev")

    # Initial Build
    Console.info("ŋ compile...")
    Builder().build()

    # Ports
    run_host = host or getattr(config, "useHost", "0.0.0.0")
    base_port = port or getattr(config, "usePort", 3000)
    server_port, client_port = generate_port(run_host, base_port)

    # État des processus
    api_proc = None
    vite_proc = None

    def restart_api():
        """Tue l'ancien Uvicorn et en lance un nouveau."""
        nonlocal api_proc
        if api_proc:
            api_proc.terminate()
            try:
                api_proc.wait(timeout=2)
            except:
                api_proc.kill()
        
        api_proc = Server.uvicorn(host=run_host, port=server_port, as_process=True)

    # Initialisation du Watcher avec le callback de restart
    observer = create_observer(
        path=".", 
        patterns=config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=restart_api
    )

    try:
        # Lancement initial des services
        restart_api()
        
        if getattr(config, "useVite", False):
            vite_proc = Server.vite(port=client_port)

        # Boucle de maintien
        while True:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        Console.warn("\nŋ dev server stopped")
    finally:
        observer.stop()
        observer.join()
        if api_proc: api_proc.terminate()
        if vite_proc: vite_proc.terminate()
        Console.success("Watcher stopped.")