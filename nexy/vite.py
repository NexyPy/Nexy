import os
import json
from pathlib import Path
from nexy.utils.ports import get_client_port


def Vite():
    if not os.path.exists("vite.config.ts"):
        raise FileNotFoundError("vite.config.ts not found")
    manifest_path = Path("__nexy__/client/.vite/manifest.json")
    if manifest_path.is_file():
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
            if isinstance(entry, dict) and "file" in entry:
                src = "/__nexy__/client/" + entry["file"].lstrip("/")
                return f'<script type="module" src="{src}"></script>'
        except Exception:
            pass
    port = get_client_port(5173)
    base = f"http://localhost:{port}"
    client = f'<script type="module" src="{base}/@vite/client"></script>'
    entry = f'<script type="module" src="{base}/__nexy__/main.ts"></script>'
    return f"{client}{entry}"
