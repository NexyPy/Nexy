import subprocess
import shutil
from pathlib import Path
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