from typing import Optional
from nexy.__version__ import __Version__
from nexy.cli.commands.utilities.console import console
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server

def start(port: Optional[int] = None, host: Optional[str] = None) -> None:
    # 1. Initialisation et vérification
    version = __Version__().get()
    Server.check_nexy_prod()
    
    config = Config()
    run_host = host or getattr(config, "useHost", "0.0.0.0")
    run_port = Server.resolve_port(run_host, port or getattr(config, "usePort", 3000))

    # 2. Affichage du header
    console.print(f"nexy@{version} [dim]starting in production...[/dim]\n")

    console.print(f"  [dim]»»[/dim] [green]Uvicorn[/green] running on port [yellow]{run_port}[/yellow]")
    console.print(f"  [dim]»»[/dim] Local:   [green]http://localhost:{run_port}[/green]")
    if run_host != "127.0.0.1" and run_host != "localhost":
        console.print(f"  [dim]»»[/dim] Network: [green]http://{run_host}:{run_port}[/green]")
    
    console.print(f"  [dim]»»[/dim] Press [dim]Ctrl+C[/dim] to stop\n")

    try:
        Server.uvicorn(host=run_host, port=run_port)
    except KeyboardInterrupt:
        console.print("\n[yellow]nexy » stopping server...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]✘ Error starting server:[/red] {e}")
    