import logging
import time
from typing import Optional
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server
from nexy.cli.commands.utilities.watcher import create_observer
from nexy.cli.commands.utilities.console import console
from nexy.utils.ports import generate_port

def dev(port: Optional[int] = None, host: Optional[str] = None) -> None:
    config = Config()
    version = __Version__().get()
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
        console.print(f"nexy@{version} dev using : \n")
        restart_api()
        
        if getattr(config, "useVite", False):
            vite_proc = Server.vite(port=client_port)

        console.print(f"  [dim]»»[/dim] [green]Uvicorn[/green] on port [green]{server_port}[/green]")
        if vite_proc:
            console.print(f"  [dim]»»[/dim] [green]Vite[/green] on port [green]{client_port}[/green]")
        console.print(f"  [dim]»»[/dim] Local: [green]http://localhost:{server_port}[/green]")
        # console.print(f"  - Network: [green]http://{run_host}:{server_port}[/green]")

        with console.status("\n[green]nsc[/green] » compile...", spinner="dots"):
            start_time = time.perf_counter()
            Builder().build()
            elapsed = time.perf_counter() - start_time
            timer = f"{elapsed:.2f}s"
            time.sleep(.03)
            console.print(f"\n[green]nsc[/green] » [green]compiling[/green] in [reset][dim]{timer}[/dim] [green]✓[/green]")

        while True:
            time.sleep(1)

    except (KeyboardInterrupt, SystemExit):
        pass
        # Console.warn("\nŋ dev server stopped")
        pass
    finally:
        observer.stop()
        observer.join()
        if api_proc: api_proc.terminate()
        if vite_proc: vite_proc.terminate()
        print("nexy » exited")