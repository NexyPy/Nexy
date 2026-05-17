import subprocess
import shutil
import socket
import sys
from pathlib import Path
from typing import Any, Optional, Tuple
from subprocess import Popen
import uvicorn as _uvicorn

from nexy.core.config import Config
from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG
from nexy.cli.commands.utilities.console import console as print_console

_NEXY_DIR = Path("__nexy__")

# ── Port utilities ──────────────────────────────────────────────────────────

def _is_port_available(host: str, port: int) -> bool:
    """
    Vérifie si un port est libre en combinant une tentative de connexion 
    et un fallback par binding.
    """
    # Étape 1 : Tentative de connexion (détecte si un service écoute)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        try:
            sock.connect((host, port))
            return False  # Si on peut se connecter, le port est occupé
        except (ConnectionRefusedError, socket.timeout):
            pass 
        except OSError:
            pass

    # Étape 2 : Tentative de Binding (confirmation finale)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # SO_REUSEADDR permet de réutiliser le port sans attendre le timeout kernel
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            return True # Bind réussi, le port est libre
        except OSError:
            return False

def find_available_port(
    start_port: int,
    host: str = "127.0.0.1",
    max_attempts: int = 100,
) -> int:
    """Parcourt les ports jusqu'à en trouver un de libre."""
    for port in range(start_port, start_port + max_attempts):
        if _is_port_available(host, port):
            return port
    raise RuntimeError(f"Aucun port disponible trouvé sur {host} aux alentours de {start_port}")

# ── Internal helpers ────────────────────────────────────────────────────────

def _write_port_file(name: str, port: int) -> None:
    """Enregistre le port utilisé pour la communication inter-processus."""
    _NEXY_DIR.mkdir(exist_ok=True)
    (_NEXY_DIR / f"{name}.port").write_text(str(port), encoding="utf-8")

def _detect_pm() -> Tuple[str, bool]:
    """Détecte le gestionnaire de paquets (pnpm, bun, yarn, npm)."""
    for candidate in ("pnpm", "bun", "yarn", "npm"):
        binary = shutil.which(candidate) or shutil.which(candidate + ".cmd")
        if binary:
            return binary, candidate == "npm"
    return "npm", True

# ── Server class ────────────────────────────────────────────────────────────

class Server:

    @staticmethod
    def check_nexy_prod(delete: bool = False) -> None:
        path = _NEXY_DIR / "nexy.prod"
        if delete:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("1", encoding="utf-8")

    @staticmethod
    def resolve_ports(
        host: Optional[str] = None,
        port: Optional[int] = None,
    ) -> Tuple[int, int]:
        """
        Calcule les ports du serveur et du client en cascade.
        Retourne (server_port, client_port).
        """
        cfg = Config()
        run_host: str = host or getattr(cfg, "host", "127.0.0.1")
        base_port: int = port or getattr(cfg, "port", 3000)

        # 1. On trouve un port pour le serveur (ex: 3000 ou 3001)
        server_port = find_available_port(base_port, run_host)
        
        # 2. On trouve un port pour le client (doit être différent du serveur)
        # On commence la recherche juste après le port serveur
        client_port = find_available_port(server_port + 1, run_host)

        return server_port, client_port

    @staticmethod
    def uvicorn(
        host: Optional[str] = None,
        port: int = 3000,
        as_process: bool = False,
    ) -> Optional[Popen[Any]]:
        """Lance le serveur FastAPI/Uvicorn."""
        run_host = host or "127.0.0.1"
        
        _write_port_file("server", port)

        try:
            if as_process:
                # On écrit un petit script Python "à la volée"
                launcher_code = (
                    "import uvicorn\n"
                    "import sys\n"
                    "try:\n"
                    "    from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG\n"
                    f"    uvicorn.run('nexy.routers.app:_server', host='{run_host}', port={port}, "
                    "log_config=NEXY_LOG_CONFIG, log_level='info')\n"
                    "except Exception as e:\n"
                    "    print(f'Critical error in Nexy subprocess: {e}')\n"
                    "    sys.exit(1)\n"
                )

                return subprocess.Popen(
                    [sys.executable, "-c", launcher_code],
                    stdout=None,
                    stderr=subprocess.STDOUT,
                )
            else:
                _uvicorn.run('nexy.routers.app:_server', host=host, port= port, log_config=NEXY_LOG_CONFIG, log_level='info')
                return True
            
                
        except Exception as exc:
            print_console.print(f"[red]✘ Échec du lancement du serveur :[/red] {exc}")
            return None

    @staticmethod
    def vite(
        port: int = 5173,
        build: bool = False,
    ) -> Popen[Any]:
        """Lance le client Vite."""
        pm, is_npm = _detect_pm()
        cmd = "build" if build else "dev"

        args = [pm, "--silent"]
        args += ["run", cmd] if is_npm else [cmd]

        if not build:
            _write_port_file("client", port)
            if is_npm:
                args.append("--")
            args += ["--port", str(port), "--host"]
            
        return subprocess.Popen(args)