import markdown
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Any, Dict, Optional
from pathlib import Path
import json
from .core.config import Config
from .utils.server.ports import get_vite_port

extension_configs={
    "pymdownx.highlight": {
    "pygments_lang_class": True,
    "linenums": False, 
    }
}

class Template:
    """Class to handle Jinja2 and Markdown template rendering."""
    
    def __init__(self, templates_dir: str = ".") -> None:
        """Initialize the renderer with Nexy configuration."""
        self.config = Config()
        self.templates_dir = templates_dir
        
        # Security: autoescape prevents XSS
        self.env = Environment(
            loader=FileSystemLoader(templates_dir),
            auto_reload=True,
            # autoescape=select_autoescape(['html', 'xml'])
        )
    
    def _render_jinja2(self, path: str, context: Dict[str, Any]) -> str:
        """Loads and renders a Jinja2 template."""
        template = self.env.get_template(path)
        return template.render(context)
    
    def _render_markdown(self, content: str) -> str:
        """Convert Markdown text to HTML."""
        # Use the standard 'markdown' library with common extensions
        return markdown.markdown(content, extensions=self.config.MARKDOWN_EXTENSIONS, extension_configs=extension_configs)
    
    def render(self, path: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Renders a template according to the extension (Jinja2 or Markdown).
        
        Args:
            path: Path to the template
            context: Context for rendering (key-value dict)
        
        Returns:
            Rendered content (HTML)
        """
        if context is None:
            context = {}
        
        rendered_content = self._render_jinja2(path, context)

        if path.endswith(".md"):
            return self._render_markdown(rendered_content)
        return rendered_content
