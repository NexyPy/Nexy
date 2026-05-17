import os
import json
from pathlib import Path
from nexy.core.config import Config
from nexy.utils.ports import get_client_port


def Vite() -> str:
    # 1. Vérification config
    config = Config()
    if not os.path.exists("vite.config.ts"):
        return "" # Pas de Vite si pas de config
    
    if not getattr(config, "useVite", False):
        return "" # Pas de Vite si désactivé

    manifest_path = Path("__nexy__/client/.vite/manifest.json")
    prod_server = Path("__nexy__/nexy.prod")
    prod_mode = manifest_path.is_file() and prod_server.is_file()
    if prod_mode:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
            if entry and "file" in entry:
                file_rel = entry["file"].lstrip("/")
                css_files = entry.get("css") or []
                inline = os.getenv("NEXY_INLINE_CLIENT", "").strip() in ("1", "true", "TRUE")
                if inline:
                    # Inline CSS and JS content to avoid extra HTTP requests
                    css_blocks = []
                    for c in css_files:
                        p = Path("__nexy__/client").joinpath(c.lstrip("/"))
                        if p.is_file():
                            css_blocks.append(f"<style>{p.read_text(encoding='utf-8')}</style>")
                    js_path = Path("__nexy__/client").joinpath(file_rel)
                    js_code = js_path.read_text(encoding="utf-8") if js_path.is_file() else ""
                    return "".join(css_blocks) + f'<script type="module">\n{js_code}\n</script>'
                else:
                    # src = f"/__nexy__/client/{file_rel}"
                    src = f"/{file_rel}"
                    css_links = "".join(
                        f"<link rel=\"stylesheet\" href=\"/{c.lstrip('/')}\" />"
                        # f"<link rel=\"stylesheet\" href=\"/__nexy__/client/{c.lstrip('/')}\" />"
                        for c in css_files
                    )
                    return f'{css_links}<script type="module" src="{src}"></script>'
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
