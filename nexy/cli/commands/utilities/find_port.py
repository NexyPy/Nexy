import socket
from typing import Optional

def find_port(start: int = 3000, host: Optional[str] = None, limit: int = 1000) -> int:
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
