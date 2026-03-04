import os
import json
from pathlib import Path
from nexy.utils.ports import get_client_port


def Vite():
    # 1. Vérification config
    if not os.path.exists("vite.config.ts"):
        raise FileNotFoundError("vite.config.ts not found")

    manifest_path = Path("__nexy__/client/.vite/manifest.json")
    prod_server = Path("__nexy__/nexy.prod")
    prod_mode = manifest_path.is_file() and prod_server.is_file()
    if prod_mode:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
            css = entry.get("css")
            if entry and "file" in entry:
                src = f"/__nexy__/client/{entry['file'].lstrip('/')}"
                csssrc = f"<style>@import url('/__nexy__/client/{css[0].lstrip('/')}');</style>"
                return f'{csssrc}<script type="module" src="{src}"></script>'
        except Exception:
            pass
    if prod_server.is_file() is True and manifest_path.is_file() is False:
        raise FileNotFoundError("manifest.json not found")
    # 3. Mode Développement (Dynamique via le navigateur)
    port = get_client_port(5173)
    
    # On utilise un petit script JS pour injecter les balises avec le bon hostname
    return f"""
    <script type="module">
        const host = window.location.hostname;
        const base = `http://${{host}}:{port}`;
        
        const s1 = document.createElement('script');
        s1.type = 'module';
        s1.src = `${{base}}/@vite/client`;
        document.head.appendChild(s1);
        
        const s2 = document.createElement('script');
        s2.type = 'module';
        s2.src = `${{base}}/__nexy__/main.ts`;
        document.head.appendChild(s2);
    </script>
    """

