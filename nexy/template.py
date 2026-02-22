import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any, Dict, Optional
from pathlib import Path
import json
from .core.config import Config
from .utils.ports import get_vite_port, is_port_open


class Template:
    """Classe pour gérer le rendu des templates Jinja2 et Markdown."""
    
    def __init__(self):
        """Initialise le renderer avec la configuration Nexy."""
        self.config =  Config()
        
        # Sécurité : autoescape activé pour éviter les failles XSS
        self.env = Environment(
            loader=FileSystemLoader("."),
            auto_reload=True,
        
        )
    
    def _render_jinja2(self, path: str, context: Dict[str, Any]) -> str:
        """Charge et rend un template Jinja2."""
        template = self.env.get_template(path)
        return template.render(context)
    
    def _render_markdown(self, content: str) -> str:
        """Convertit le texte Markdown en HTML."""
        # Utilisation de la librairie standard 'markdown' avec extensions communes
        return markdown.markdown(content, extensions=self.config.MARKDOWN_EXTENSIONS)
    
    def render(self, path: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Rend un template selon l'extension (Jinja2 ou Markdown).
        
        Args:
            path: Chemin du template
            context: Contexte pour le rendu (dict clé-valeur)
        
        Returns:
            Contenu rendu (HTML)
        """
        if context is None:
            context = {}
        
        rendered_content = self._render_jinja2(path, context)

        if path.endswith(".md"):
            return self._render_markdown(rendered_content)
        
        scripts: list[str] = []
        is_dev = bool(getattr(self.config, "useVite", False))
        if is_dev:
            vite_port = get_vite_port(5173)
            if not is_port_open("127.0.0.1", vite_port):
                return rendered_content
            base = f"http://localhost:{vite_port}"
            scripts.append(f'<script type="module" src="{base.rstrip("/")}/@vite/client"></script>')
            scripts.append(f'<script type="module" src="{base.rstrip("/")}/__nexy__/main.ts"></script>')
        else:
            manifest_path = Path("__nexy__/client/.vite/manifest.json")
            if manifest_path.is_file():
                try:
                    data = json.loads(manifest_path.read_text(encoding="utf-8"))
                    entry = data.get("__nexy__/main.ts") or data.get("/__nexy__/main.ts")
                    if isinstance(entry, dict) and "file" in entry:
                        src = "/__nexy__/client/" + entry["file"].lstrip("/")
                        scripts.append(f'<script type="module" src="{src}"></script>')
                except Exception:
                    pass
        if scripts:
            bundle = "".join(scripts)
            lower = rendered_content.lower()
            idx = lower.rfind("</body>")
            if idx != -1:
                rendered_content = rendered_content[:idx] + bundle + rendered_content[idx:]
            else:
                rendered_content = rendered_content + bundle
        return rendered_content
