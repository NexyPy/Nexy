from dataclasses import dataclass, field
from typing import List, Dict, Optional, Union

@dataclass
class Node:
    """Base class for all AST nodes."""
    pass

@dataclass
class TextNode(Node):
    """Represents raw text or HTML."""
    content: str

@dataclass
class ElementNode(Node):
    """Represents an HTML element or a Nexy component."""
    tag_name: str
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List[Node] = field(default_factory=list)
    is_self_closing: bool = False

    def is_component(self) -> bool:
        """Returns True if the tag starts with an uppercase letter (PascalCase)."""
        if not self.tag_name:
            return False
        # Avoid matching our internal Jinja2 placeholders (NXYPJ...)
        if self.tag_name.startswith("NXYPJ") and self.tag_name.endswith("Z"):
            return False
        return self.tag_name[0].isupper()
