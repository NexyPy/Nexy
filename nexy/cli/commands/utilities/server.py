import subprocess
import shutil
from pathlib import Path
import sys
from typing import Optional
import uvicorn as _uvicorn
from nexy.core.config import Config
from nexy.cli.commands.utilities.find_port import find_port
from nexy.utils.ports import get_client_port





class Server:
    @staticmethod
    def resolve_port(host: Optional[str] = None, port: Optional[int] = None) -> int:
        cfg = Config()
        if port is not None: return port
        run_host = host if host is not None else getattr(cfg, "useHost", "0.0.0.0")
        selected = getattr(cfg, "usePort", None) or find_port(3000, run_host)
        
        # Éviter le conflit avec Vite
        vite_port = None
        for name in ("__nexy__/client.port", "__nexy__/vite.port"):
            p = Path(name)
            if p.is_file():
                try:
                    vite_port = int(p.read_text(encoding="utf-8").strip())
                    break
                except: continue
        
        if vite_port is not None and vite_port == selected:
            selected = find_port(selected + 1, run_host)
        return selected

    @staticmethod
    def uvicorn(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False, as_process: bool = False) -> Optional[subprocess.Popen]:
        run_host = host or "127.0.0.1"
        run_port = port or 3000
        
        # On s'assure que le dossier temporaire existe pour d'autres usages
        Path("__nexy__").mkdir(exist_ok=True)

        if as_process:
            # On génère un mini-script pour lancer uvicorn avec la config importée
            # Cela permet de garder les classes (Filter/Formatter) actives
            launcher_code = (
                "import uvicorn\n"
                "from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG\n"
                f"uvicorn.run('nexy.routers.app:_server', host='{run_host}', port={run_port}, "
                "log_config=NEXY_LOG_CONFIG, log_level='info')"
            )
            
            return subprocess.Popen([sys.executable, "-c", launcher_code])
        
        else:
            # Import local pour éviter les cycles d'import si nécessaire
            from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG
            
            _uvicorn.run(
                "nexy.routers.app:_server", 
                host=run_host, 
                port=run_port, 
                log_config=NEXY_LOG_CONFIG,
                log_level="info" # On force info car notre filtre s'occupe du reste
            )
            return None

    def vicorn(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False, as_process: bool = False) -> Optional[subprocess.Popen]:
        """
        Lance Uvicorn. Si as_process=True, retourne un objet Popen non-bloquant.
        """
        run_host = host if host is not None else getattr(Config(), "useHost", "0.0.0.0")
        run_port = port or Server.resolve_port(run_host, None)
        
        Path("__nexy__").mkdir(exist_ok=True)
        with open("__nexy__/server.port", "w") as f:
            f.write(str(run_port))

        if as_process:
            # On utilise sys.executable pour garantir d'utiliser le même interpréteur Python
            import sys
            cmd = [
                sys.executable, "-m", "uvicorn", 
                "nexy.routers.app:_server", 
                "--host", run_host, 
                "--port", str(run_port)
            ]
            return subprocess.Popen(cmd)
        else:
            _uvicorn.run("nexy.routers.app:_server", host=run_host, port=run_port, reload=reload)
            return None

    @staticmethod
    def vite(port: Optional[int] = None) -> subprocess.Popen:
        vite_port = port or get_client_port(5173)
        pm = next((c for c in ("pnpm", "bun", "yarn", "npm.cmd", "npm") if shutil.which(c)), "npm")
        
        args = [pm, "run", "dev", "--", "--port", str(vite_port)]
        if pm in ("pnpm", "yarn"):
            args = [pm, "dev", "--port", str(vite_port)]
            
        return subprocess.Popen(args)