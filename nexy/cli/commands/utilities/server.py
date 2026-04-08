import subprocess
import shutil
from pathlib import Path
import sys
from typing import Optional
import uvicorn as _uvicorn
from nexy.core.config import Config
from nexy.cli.commands.utilities.find_port import find_port
from nexy.utils import console
from nexy.utils.ports import get_client_port





class Server:
    @staticmethod
    def check_nexy_prod(delete: bool = False):
        path = Path("__nexy__/nexy.prod")
        if delete:
            path.unlink(missing_ok=True)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("1", encoding="utf-8")
            
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
        
        try:
            # Ensure temporary directory exists
            Path("__nexy__").mkdir(exist_ok=True)

            if as_process:
                # Generate a mini-launcher to preserve Nexy's logging configuration
                launcher_code = (
                    "import uvicorn\n"
                    "try:\n"
                    "    from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG\n"
                    f"    uvicorn.run('nexy.routers.app:_server', host='{run_host}', port={run_port}, "
                    "log_config=NEXY_LOG_CONFIG, log_level='info')\n"
                    "except Exception as e:\n"
                    "    print(f'Critical error in Nexy subprocess: {e}')\n"
                )
                
                return subprocess.Popen(
                    [sys.executable, "-c", launcher_code],
                    stdout=None,  # Inherit terminal for direct logging
                    stderr=subprocess.STDOUT
                )
            
            else:
                # Blocking mode (Standard)
                try:
                    from nexy.cli.commands.utilities.uvicorn_config import NEXY_LOG_CONFIG
                    
                    _uvicorn.run(
                        "nexy.routers.app:_server", 
                        host=run_host, 
                        port=run_port, 
                        log_config=NEXY_LOG_CONFIG,
                        log_level="info"
                    )
                except ImportError:
                    console.print("[red]✘ Error:[/red] Could not find [bold]NEXY_LOG_CONFIG[/bold].")
                except Exception as e:
                    console.print(f"[red]✘ Server launch failed:[/red] {e}")
                
                return None

        except PermissionError:
            console.print(f"[red]✘ Error:[/red] Insufficient permissions to create [bold]__nexy__[/bold] directory.")
        except Exception as e:
            console.print(f"[red]✘ An unexpected error occurred:[/red] {e}")
            return None

    @staticmethod
    def vite(port: Optional[int] = None, build: bool = False) -> subprocess.Popen:
        pm = next((c for c in ("pnpm", "bun", "yarn", "npm.cmd", "npm") if shutil.which(c)), "npm")
        is_npm = pm not in ("pnpm", "yarn", "bun")
        cmd = "build" if build else "dev"
        

        args = [pm, "--silent"]
        if is_npm:
            args.extend(["run", cmd])
        else:
            args.append(cmd)
            
        if not build:
            vite_port = port or get_client_port(5173)
            if is_npm:
                args.append("--")
            args.extend(["--port", str(vite_port), "--host"])
                
        return subprocess.Popen(args)
