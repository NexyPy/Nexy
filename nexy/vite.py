import os
from nexy.utils.ports import get_vite_port, is_port_open


def Vite():
    port = get_vite_port(5173)
    if not os.path.exists("vite.config.ts"):
        raise FileNotFoundError("vite.config.ts not found")
    if not is_port_open("127.0.0.1", int(port)):
        return ""
    base = f"http://localhost:{port}"
    client = f'<script type="module" src="{base}/@vite/client"></script>'
    entry = f'<script type="module" src="{base}/__nexy__/main.ts"></script>'
    return f"{client}{entry}"
