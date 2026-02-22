import socket
from pathlib import Path
from typing import Optional


def _read_port_file(path: str) -> Optional[int]:
    p = Path(path)
    if not p.is_file():
        return None
    try:
        txt = p.read_text(encoding="utf-8").strip()
        n = int(txt)
        return n if n > 0 else None
    except Exception:
        return None


def get_server_port(default: int = 3000) -> int:
    n = _read_port_file("__nexy__/server.port")
    return n if n is not None else default


def get_vite_port(default: int = 5173) -> int:
    n = _read_port_file("__nexy__/vite.port")
    return n if n is not None else default


def is_port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

