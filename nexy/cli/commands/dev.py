import time

from nexy.__version__ import __Version__
from nexy.builder import Builder
from nexy.core.config import Config
from nexy.frontend import FrontendGenerator
from nexy.utils.common.console import console
from nexy.utils.dev.watcher import create_observer
from nexy.utils.server.server import Server


def dev(port: int | None = None, host: str | None = None) -> None:
    config = Config()
    version = __Version__().get()
    run_host = host or config.useHost
    if port:
        run_port = port
    else:
        run_port, client_port = Server.resolve_ports(run_host, port or config.usePort)
    Server.check_nexy_prod(delete=True)

    vite_proc = None
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    def hmr_signal() -> None:
        """Signal that a reload happened (optional)."""
        # With true HMR, we don't need to restart anything.
        # Just logging or notifying the browser via WebSocket could happen here.
        pass

    startup_start = time.perf_counter()

    try:
        # Initial build (to VFS)
        with console.status("\n[green]nsc[/green] » compile...", spinner="dots"):
            build_start = time.perf_counter()
            result = Builder().build()
            build_elapsed = time.perf_counter() - build_start
            build_timer = f"{build_elapsed:.2f}s"
            console.print(
                "\n[green]nsc[/green] » [green]compiling[/green]"
                f" in [reset][dim]{build_timer}[/dim]"
            )
            if result.failed:
                for p in result.failed:
                    console.print(f"  [red]x {p}[/red]")

        if not result.failed:
            FrontendGenerator().generate()
            if config.useVite:
                vite_proc = Server.vite(port=client_port, ssl=ssl_enabled)
                time.sleep(0.05)
    except Exception as e:
        console.print(f"\n[red]Error during initialization:[/red] {e}")
        vite_proc = None

    # Watcher initialization (now handles in-memory HMR)
    observer = create_observer(
        path=".",
        patterns=config.WATCH_EXTENSIONS_GLOB,
        ignore_patterns=config.WATCH_EXCLUDE_PATTERNS,
        on_reload_api=hmr_signal,
    )

    startup_elapsed = time.perf_counter() - startup_start
    startup_timer = f"{startup_elapsed:.2f}s"

    network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host

    try:
        console.print(f"nexy@{version} dev using : \n")
        console.print(f"  [dim]»»[/dim] [green]Uvicorn[/green] on port [green]{run_port}[/green]")
        if vite_proc:
            console.print(
                f"  [dim]»»[/dim] [green]Vite[/green] on port [green]{client_port}[/green]"
            )
        console.print(f"  [dim]»»[/dim] Local: [green]{protocol}://localhost:{run_port}[/green]")
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            console.print(
                f"  [dim]»»[/dim] Network: [green]{protocol}://{network_ip}:{run_port}[/green]"
            )
        console.print(f"  [dim]»»[/dim] ready in [green]{startup_timer}[/green]")
        console.print("  [dim]»»[/dim] press [dim]Ctrl+C[/dim] to stop")

        # Start Uvicorn in the SAME process (blocks)
        # This ensures they share the same VFS and sys.modules
        Server.uvicorn(
            host=run_host,
            port=run_port,
            as_process=False,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )

    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        observer.stop()
        observer.join()
        if vite_proc:
            vite_proc.terminate()
        console.print("[red]nexy » exited [reset]")
