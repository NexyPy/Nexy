from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.utils.common.console import console
from nexy.utils.server.server import Server


def start(port: int | None = None, host: str | None = None) -> None:
    # 1. Initialization and verification
    version = __Version__().get()
    # Server.check_nexy_prod()

    config = Config()
    run_host = host or config.useHost
    run_port, _ = Server.resolve_ports(run_host, port or config.usePort)

    try:
        console.print(f"nexy@{version} [dim]starting in production...[/dim]\n")

        console.print(
            f"  [dim]»»[/dim] [green]Uvicorn[/green] running on port [yellow]{run_port}[/yellow]"
        )
        console.print(f"  [dim]»»[/dim] Local:   [green]http://localhost:{run_port}[/green]")
        if run_host != "127.0.0.1" and run_host != "localhost":
            console.print(f"  [dim]»»[/dim] Network: [green]http://{run_host}:{run_port}[/green]")

        console.print("  [dim]»»[/dim] Press [dim]Ctrl+C[/dim] to stop\n")

        Server.uvicorn(host=run_host, port=run_port)

    except (KeyboardInterrupt, SystemExit):
        console.print("[red]nexy » exited [reset]")
    finally:
        console.print("[red]nexy » exited [reset]")
