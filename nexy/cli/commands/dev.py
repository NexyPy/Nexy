import logging
import time
from typing import Optional
from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server
from nexy.cli.commands.utilities.watcher import create_observer
from nexy.frontend import FrontendGenerator
from nexy.utils.console import console
from nexy.utils.ports import generate_port

def dev(port: Optional[int] = None, host: Optional[str] = None) -> None:
    config = Config()
    version = __Version__().get()
    run_host = host or getattr(config, "useHost", "0.0.0.0")
    if port:
        run_port = port
    else:
        run_port, client_port = Server.resolve_ports(run_host, port or getattr(config, "usePort", 3000))
    Server.check_nexy_prod(delete=True)
    api_proc = None
    vite_proc = None

    def restart_api() -> None:
        """Tue l'ancien Uvicorn et en lance un nouveau."""
        nonlocal api_proc
        if api_proc:
            api_proc.terminate()
            try:
                api_proc.wait(timeout=2)
            except:
                api_proc.kill()
        
        api_proc = Server.uvicorn(host=run_host, port=run_port, as_process=True)

    try:
        FrontendGenerator().generate()
        if getattr(config, "useVite", False):
            vite_proc = Server.vite(port=client_port)
            time.sleep(.05)
    except Exception as e:
        console.print(f"\n[red]✘ Error starting Vite:[/red] {e}")
        vite_proc = None
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

        console.print(f"  [dim]»»[/dim] [green]Uvicorn[/green] on port [green]{run_port}[/green]")
        if vite_proc:
            console.print(f"  [dim]»»[/dim] [green]Vite[/green] on port [green]{client_port}[/green]")
        console.print(f"  [dim]»»[/dim] Local: [green]http://localhost:{run_port}[/green]")
        console.print(f"  [dim]»»[/dim] press [dim]Ctrl+C[/dim] to stop")
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

    except (KeyboardInterrupt, SystemExit) as e:
        pass
    finally:
        observer.stop()
        observer.join()
        if api_proc: api_proc.terminate()
        if vite_proc: vite_proc.terminate()
        console.print("[red]nexy » exited [reset]")
