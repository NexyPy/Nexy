import logging
from  os import system, path
import subprocess
from sys import platform
import typer
from rich.prompt import  IntPrompt


from nexy.cli.core.constants import Console,CMD
from nexy.cli.core.utils import get_next_available_port, print_banner


@CMD.command()
def serve(
    port: int = typer.Option(3000, "--port", "-p", help="Port du serveur"),
    host: str = typer.Option("localhost", "--host", help="Host du serveur"),
    worker : int = typer.Option(1)
)-> None:
    """Lance le serveur"""
    # print(NEXY_CONFIGS.PORT)
    port = get_next_available_port(port)
    print_banner()
    Console.print(f"[green]Server started on [yellow]http://{host}:{port}[/yellow][/green]")
    
    system(f"uvicorn nexy-config:run --host {host} --port {port} --reload --log-level debug")
    # subprocess.run(f" uvicorn nexy-config:app --host {host} --port {port} --reload --log-level debug  --use-colors ", check=True)
    

def add(package: str):
    # Devrait utiliser le pip de l'environnement virtuel nexy_env
    if path.exists("nexy_env"):
        pip_path = "nexy_env/Scripts/pip" if platform == "win32" else "nexy_env/bin/pip"
        system(f"{pip_path} install {package}")
    else:
        system(f"pip install {package}")

