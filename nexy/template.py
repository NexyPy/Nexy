import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any, Dict, Optional
from .core.config import Config


class Template:
    """Classe pour gérer le rendu des templates Jinja2 et Markdown."""
    
    def __init__(self):
        """Initialise le renderer avec la configuration Nexy."""
        self.config =  Config()
        
        # Sécurité : autoescape activé pour éviter les failles XSS
        self.env = Environment(
            loader=FileSystemLoader("."),
            autoescape=select_autoescape(["html", "xml"]),
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
        
        # 1. Rendu Jinja (interpolation des variables)
        rendered_content = self._render_jinja2(path, context)
        
        # 2. Traitement post-rendu selon l'extension
        if path.endswith(".md"):
            return self._render_markdown(rendered_content)
        
        # Par défaut (html ou autres), on retourne le contenu rendu par Jinja
        return rendered_content
