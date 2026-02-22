from typing import Optional
from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.cli.commands.utilities.server import Server


def start(port: Optional[int] = None, host: Optional[str] = None, reload: bool = False) -> None:
    version = __Version__().get()
    print(f"> nexy@{version} start")
    config = Config()
    run_host = host if host is not None else getattr(config, "useHost", "0.0.0.0")
    run_port = Server.resolve_port(run_host, port)
    Server.uvicorn(host=run_host, port=run_port, reload=reload)
