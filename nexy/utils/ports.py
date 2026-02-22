import socket
from pathlib import Path
from typing import Optional, Tuple


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


def _find_port(start: int, host: str, limit: int = 1000) -> int:
    h = host or "0.0.0.0"
    p = start
    end = start + max(1, limit)
    while p < end:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind((h, p))
            s.close()
            return p
        except OSError:
            s.close()
            p += 1
    return start


def generate_port(host: str, base_port: Optional[int] = None, default_port: int = 3000) -> Tuple[int, int]:
    if base_port is not None and base_port > 0:
        server_port = base_port
    else:
        server_port = _find_port(default_port, host)
    client_port = _find_port(server_port + 1, host)
    Path("__nexy__").mkdir(parents=True, exist_ok=True)
    Path("__nexy__/server.port").write_text(str(server_port), encoding="utf-8")
    Path("__nexy__/client.port").write_text(str(client_port), encoding="utf-8")
    return server_port, client_port


def get_server_port(default: int = 3000) -> int:
    n = _read_port_file("__nexy__/server.port")
    return n if n is not None else default


def get_client_port(default: int = 5173) -> int:
    n = _read_port_file("__nexy__/client.port")
    if n is None:
        n = _read_port_file("__nexy__/vite.port")
    return n if n is not None else default


def get_vite_port(default: int = 5173) -> int:
    return get_client_port(default)


def is_port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False
