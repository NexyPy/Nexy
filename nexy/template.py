import os
from typing import Any

import markdown
from jinja2 import BaseLoader, Environment, TemplateNotFound

from nexy.utils.fs.vfs import VFS

from .core.config import Config

extension_configs = {
    "pymdownx.highlight": {
        "pygments_lang_class": True,
        "linenums": False,
    }
}


class NexyVFSLoader(BaseLoader):
    """Jinja2 loader that reads from the VFS."""

    def __init__(self) -> None:
        self.vfs = VFS()

    def get_source(self, environment, template):
        if not self.vfs.exists(template):
            # Fallback to filesystem if not in VFS (e.g. for user templates)
            if os.path.exists(template):
                with open(template, encoding="utf-8") as f:
                    return f.read(), template, lambda: True
            raise TemplateNotFound(template)

        source = self.vfs.read(template)
        return source, template, lambda: True


class Template:
    """Class to handle Jinja2 and Markdown template rendering."""

    def __init__(self, templates_dir: str = ".") -> None:
        """Initialize the renderer with Nexy configuration."""
        self.config = Config()
        self.templates_dir = templates_dir

        # Security: autoescape prevents XSS
        self.env = Environment(
            loader=NexyVFSLoader(),
            auto_reload=True,
        )

    def _render_jinja2(self, path: str, context: dict[str, Any]) -> str:
        """Loads and renders a Jinja2 template."""
        template = self.env.get_template(path)
        return template.render(context)

    def _render_markdown(self, content: str) -> str:
        """Convert Markdown text to HTML."""
        # Use the standard 'markdown' library with common extensions
        return markdown.markdown(
            content, extensions=self.config.MARKDOWN_EXTENSIONS, extension_configs=extension_configs
        )

    def render(self, path: str, context: dict[str, Any] | None = None) -> str:
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
