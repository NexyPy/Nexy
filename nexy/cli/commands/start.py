import time

from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.utils.common.console import console
from nexy.utils.server.server import Server


def start(port: int | None = None, host: str | None = None) -> None:
    startup_start = time.perf_counter()
    version = __Version__().get()

    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort)
    ssl_keyfile, ssl_certfile = Server.get_ssl_config(config)
    ssl_enabled = bool(ssl_keyfile and ssl_certfile)
    protocol = "https" if ssl_enabled else "http"

    startup_elapsed = time.perf_counter() - startup_start
    startup_timer = f"{startup_elapsed:.2f}s"

    network_ip = Server.get_network_ip() if run_host == "0.0.0.0" else run_host

    try:
        console.print(f"nexy@{version} [dim]starting in production...[/dim]\n")

        console.print(
            f"  [dim]»»[/dim] [green]Uvicorn[/green] running on port [yellow]{run_port}[/yellow]"
        )
        console.print(f"  [dim]»»[/dim] Local:   [green]{protocol}://localhost:{run_port}[/green]")
        if network_ip != "127.0.0.1" and network_ip != "localhost":
            console.print(
                f"  [dim]»»[/dim] Network: [green]{protocol}://{network_ip}:{run_port}[/green]"
            )

        console.print(f"  [dim]»»[/dim] ready in [green]{startup_timer}[/green]")
        console.print("  [dim]»»[/dim] Press [dim]Ctrl+C[/dim] to stop\n")

        Server.uvicorn(
            host=run_host,
            port=run_port,
            ssl_keyfile=ssl_keyfile,
            ssl_certfile=ssl_certfile,
        )

    except (KeyboardInterrupt, SystemExit):
        console.print("[red]nexy » exited [reset]")
    finally:
        console.print("[red]nexy » exited [reset]")
