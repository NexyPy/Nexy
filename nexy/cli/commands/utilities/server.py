from typing import Optional
import subprocess
import shutil
import uvicorn as _uvicorn
from nexy.core.config import Config
from nexy.cli.commands.utilities.find_port import find_port


class Server:
    @staticmethod
    def resolve_port(host: Optional[str] = None, port: Optional[int] = None) -> int:
        cfg = Config()
        if port is not None:
            return port
        default_port = getattr(cfg, "usePort", None)
        run_host = host if host is not None else getattr(cfg, "useHost", "0.0.0.0")
        return default_port if default_port is not None else find_port(3000, run_host)
    @staticmethod
    def uvicorn(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False) -> None:
        try:
            run_host = host if host is not None else getattr(Config(), "useHost", "0.0.0.0")
            run_port = Server.resolve_port(run_host, port)
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
    def vite(port: Optional[int] = None) -> None:
        try:
            vite_port = Server.resolve_port(None, port)
            pm = None
            for candidate in ("npm.cmd", "npm", "pnpm", "yarn", "bun"):
                if shutil.which(candidate):
                    pm = candidate
                    break
            if pm is None:
                raise FileNotFoundError("Package manager not found")
            if pm in ("npm", "npm.cmd"):
                args = [pm, "run", "dev", "--", "--port", str(vite_port or 5173)]
            elif pm == "pnpm":
                args = [pm, "dev", "--port", str(vite_port or 5173)]
            elif pm == "yarn":
                args = [pm, "dev", "--port", str(vite_port or 5173)]
            else:
                args = [pm, "run", "dev", "--port", str(vite_port or 5173)]
            subprocess.call(args)
        except Exception as e:
            print(e)

    @staticmethod
    def vite_async(port: Optional[int] = None) -> subprocess.Popen:
        try:
            vite_port = Server.resolve_port(None, port)
            pm = None
            for candidate in ("npm.cmd", "npm", "pnpm", "yarn", "bun"):
                if shutil.which(candidate):
                    pm = candidate
                    break
            if pm is None:
                raise FileNotFoundError("Package manager not found")
            if pm in ("npm", "npm.cmd"):
                args = [pm, "run", "dev", "--", "--port", str(vite_port or 5173)]
            elif pm == "pnpm":
                args = [pm, "dev", "--port", str(vite_port or 5173)]
            elif pm == "yarn":
                args = [pm, "dev", "--port", str(vite_port or 5173)]
            else:
                args = [pm, "run", "dev", "--port", str(vite_port or 5173)]
            return subprocess.Popen(args)
        except Exception as e:
            print(e)
            raise


def uvicorn(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False) -> None:
    Server.uvicorn(host=host, port=port, reload=reload)


def granian(host: Optional[str] = None, port: Optional[int] = None, reload: bool = False) -> None:
    Server.granian(host=host, port=port, reload=reload)


def vite(port: Optional[int] = None) -> None:
    Server.vite(port=port)
