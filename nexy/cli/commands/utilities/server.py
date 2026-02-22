from typing import Optional
import subprocess
import shutil
from pathlib import Path
import uvicorn as _uvicorn
from nexy.core.config import Config
from nexy.cli.commands.utilities.find_port import find_port
from nexy.utils.ports import get_client_port


class Server:
    @staticmethod
    def resolve_port(host: Optional[str] = None, port: Optional[int] = None) -> int:
        cfg = Config()
        if port is not None:
            return port
        default_port = getattr(cfg, "usePort", None)
        run_host = host if host is not None else getattr(cfg, "useHost", "0.0.0.0")
        selected = default_port if default_port is not None else find_port(3000, run_host)
        vite_port = None
        for name in ("__nexy__/client.port", "__nexy__/vite.port"):
            try:
                p = Path(name)
                if p.is_file():
                    txt = p.read_text(encoding="utf-8").strip()
                    if txt:
                        vite_port = int(txt)
                        break
            except Exception:
                continue
        if vite_port is not None and vite_port == selected:
            selected = find_port(selected + 1, run_host)
        return selected

    @staticmethod
    def uvicorn(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False) -> None:
        try:
            run_host = host if host is not None else getattr(Config(), "useHost", "0.0.0.0")
            if port is not None:
                run_port = port
            else:
                run_port = Server.resolve_port(run_host, None)
            with open("__nexy__/server.port", "w") as f:
                f.write(str(run_port))
            _uvicorn.run("nexy.routers.app:_server", host=run_host, port=run_port, reload=reload)
        except Exception as e:
            print(e)

    @staticmethod
    def granian(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False) -> None:
        try:
            run_host = host if host is not None else getattr(Config(), "useHost", "0.0.0.0")
            run_port = Server.resolve_port(run_host, port)
            args = ["granian", "nexy.routers.app:_server", "--host", run_host, "--port", str(run_port)]
            if reload:
                args.append("--reload")
            subprocess.call(args)
        except Exception as e:
            print(e)

    @staticmethod
    def vite(port: Optional[int] = None) -> subprocess.Popen:
        try:
            if port is not None:
                vite_port = port
            else:
                vite_port = get_client_port(5173)
            
            pm = None
            for candidate in ("npm.cmd", "npm", "pnpm", "yarn", "bun"):
                if shutil.which(candidate):
                    pm = candidate
                    break
            if pm is None:
                raise FileNotFoundError("Package manager not found")
            if pm in ("npm", "npm.cmd"):
                args = [pm, "run", "dev", "--", "--port", str(vite_port)]
            elif pm == "pnpm":
                args = [pm, "dev", "--port", str(vite_port)]
            elif pm == "yarn":
                args = [pm, "dev", "--port", str(vite_port)]
            else:
                args = [pm, "run", "dev", "--port", str(vite_port)]
            return subprocess.Popen(args)
        except Exception as e:
            print(e)
            raise
