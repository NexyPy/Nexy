from  os import system, path
import subprocess
from sys import platform
import typer
from rich.prompt import  IntPrompt


from nexy.cli.core.constants import Console,CMD
# from nexy.cli.core.utils import display_port_choices, find_available_port, load_config, is_port_in_use, print_banner




# module = load_config()

# NEXY_CONFIGS = module.NEXY_CONFIGS or None
  

@CMD.command()
def dev(
    port: int = typer.Option(3000, "--port", "-p", help="Port du serveur"),
    host: str = typer.Option("localhost", "--host", help="Host du serveur")
)-> None:
    """Lance le serveur de développement"""
    # print(NEXY_CONFIGS.PORT)
        
    Console.print(Console.print(f"[green]🚀 Démarrage du serveur sur http://{host}:{port}[/green]"))
    
    # system(f"uvicorn nexy-config:app --host {host} --port {port} --reload --log-level debug  --use-colors ")
    print("ok")
    subprocess.run(f"uvicorn nexy-config:app --host {host} --port {port} --reload --log-level debug  --use-colors ", check=True)
    

def add(package: str):
    # Devrait utiliser le pip de l'environnement virtuel nexy_env
    if path.exists("nexy_env"):
        pip_path = "nexy_env/Scripts/pip" if platform == "win32" else "nexy_env/bin/pip"
        system(f"{pip_path} install {package}")
    else:
        system(f"pip install {package}")

