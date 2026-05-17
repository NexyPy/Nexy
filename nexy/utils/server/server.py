import shutil
import subprocess
import sys
import traceback
from pathlib import Path
from subprocess import Popen
from typing import Any

import uvicorn as _uvicorn

from nexy.core.config import Config
from nexy.utils.common.console import console as print_console
from nexy.utils.fs.vfs import VFS
from nexy.utils.server.ports import find_available_port
from nexy.utils.server.uvicorn_config import NEXY_LOG_CONFIG

_NEXY_DIR = Path("__nexy__")

# ── Internal helpers ────────────────────────────────────────────────────────


def _write_port_file(name: str, port: int) -> None:
    """Saves the port used for inter-process communication."""
    vfs = VFS()
    vfs.write(f"__nexy__/{name}.port", str(port))


def _detect_pm() -> tuple[str, bool]:
    """Detects the package manager (pnpm, bun, yarn, npm)."""
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
        host: str | None = None,
        port: int | None = None,
    ) -> tuple[int, int]:
        """
        Calculates server and client ports in cascade.
        Returns (server_port, client_port).
        """
        cfg = Config()
        run_host: str = host or cfg.useHost
        base_port: int = port or cfg.usePort

        # 1. Find a port for the server (e.g. 3000 or 3001)
        server_port = find_available_port(base_port, run_host)

        # 2. Find a port for the client (must be different from the server)
        # Search starts right after the server port
        client_port = find_available_port(server_port + 1, run_host)

        return server_port, client_port

    @staticmethod
    def uvicorn(
        host: str | None = None,
        port: int = 3000,
        as_process: bool = False,
    ) -> Popen[Any] | None:
        """Starts the FastAPI/Uvicorn server."""
        run_host = host or "127.0.0.1"

        _write_port_file("server", port)

        try:
            if as_process:
                # Writes a small Python script on the fly
                launcher_code = (
                    "import uvicorn\n"
                    "import sys\n"
                    "try:\n"
                    "    from nexy.utils.server.uvicorn_config import NEXY_LOG_CONFIG\n"
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
                _uvicorn.run(
                    "nexy.routers.app:_server",
                    host=host,
                    port=port,
                    log_config=NEXY_LOG_CONFIG,
                    log_level="info",
                )
                return True

        except Exception as exc:
            traceback.print_exc()
            print_console.print(f"[red]✘ Server launch failed:[/red] {exc}")
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
