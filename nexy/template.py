import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any, Dict, Optional
from pathlib import Path
import json
from .core.config import Config
from .utils.ports import get_vite_port


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
        return rendered_content
