import json
import os
from pathlib import Path

from nexy.core.config import Config
from nexy.utils.server.ports import get_vite_port


def Vite() -> str:
    # 1. Config verification
    config = Config()
    if not os.path.exists("vite.config.ts"):
        return ""  # No Vite if no config

    if not config.useVite:
        return ""  # No Vite if disabled

    manifest_path = Path("__nexy__/client/.vite/manifest.json")
    prod_server = Path("__nexy__/nexy.prod")
    prod_mode = prod_server.is_file()

    if prod_mode:
        if not manifest_path.is_file():
            return ""  # Prod without manifest → no Vite assets
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
            if entry and "file" in entry:
                file_rel = entry["file"].lstrip("/")
                css_files = entry.get("css") or []
                inline = os.getenv("NEXY_INLINE_CLIENT", "").strip() in ("1", "true", "TRUE")
                if inline:
                    css_blocks = []
                    for c in css_files:
                        p = Path("__nexy__/client").joinpath(c.lstrip("/"))
                        if p.is_file():
                            css_blocks.append(f"<style>{p.read_text(encoding='utf-8')}</style>")
                    js_path = Path("__nexy__/client").joinpath(file_rel)
                    js_code = js_path.read_text(encoding="utf-8") if js_path.is_file() else ""
                    return "".join(css_blocks) + f'<script type="module">\n{js_code}\n</script>'
                else:
                    src = f"/{file_rel}"
                    css_links = "".join(
                        f'<link rel="stylesheet" href="/{c.lstrip("/")}" />' for c in css_files
                    )
                    return f'{css_links}<script type="module" src="{src}"></script>'
        except Exception:
            return ""  # Malformed manifest → no Vite

    # 3. Development Mode (Dynamic via browser)
    port = get_vite_port(5173)

    # HMR Client Script
    hmr_script = """
    <script type="module">
        (function() {
            const host = window.location.host;
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${host}/_nexy/hmr`);
            
            ws.onmessage = async (event) => {
                const data = JSON.parse(event.data);
                if (data.type === 'nexy:reload') {
                    console.log(`[Nexy HMR] Reloading due to change in: ${data.path}`);
                    
                    try {
                        // 1. Fetch new HTML for current route
                        const res = await fetch(window.location.href, {
                            headers: { 'X-Nexy-HMR': '1' }
                        });
                        const html = await res.text();
                        
                        // 2. Parse and Swap Body (KISS)
                        const parser = new DOMParser();
                        const newDoc = parser.parseFromString(html, 'text/html');
                        
                        // Preserve scripts that shouldn't be re-run or handle re-hydration
                        document.body.innerHTML = newDoc.body.innerHTML;
                        
                        // 3. Re-run hydration scripts
                        const scripts = document.body.querySelectorAll('script');
                        scripts.forEach(oldScript => {
                            const newScript = document.createElement('script');
                            Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
                            newScript.appendChild(document.createTextNode(oldScript.innerHTML));
                            oldScript.parentNode.replaceChild(newScript, oldScript);
                        });

                        console.log("[Nexy HMR] DOM updated successfully.");
                    } catch (err) {
                        console.warn("[Nexy HMR] Partial reload failed, falling back to full reload.", err);
                        window.location.reload();
                    }
                }
            };

            ws.onclose = () => console.log("[Nexy HMR] Connection closed.");
        })();
    </script>
    """

    vite_protocol = "https" if config.useSslKeyfile and config.useSslCertfile else "http"

    # Small JS script to inject tags with the correct hostname
    return f"""
    {hmr_script}
    <script type="module">
        const host = window.location.hostname;
        const base = `{vite_protocol}://${{host}}:{port}`;
        
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
