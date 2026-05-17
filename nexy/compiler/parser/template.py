import re
from typing import Optional, Set

class NexyParserError(Exception):
    """Custom exception for Nexy template parsing errors."""
    pass

class TemplateFormatter:
    """Helper class to format HTML-style attributes into Python/Jinja arguments."""
    
    # Matches key = "value" with optional spaces around the '='
    _ATTR_REGEX = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')

    @classmethod
    def format_attributes(cls, attr_str: str) -> str:
        if not attr_str or not attr_str.strip():
            return ""
        
        matches = cls._ATTR_REGEX.findall(attr_str)
        pairs = []
        
        for match in matches:
            key = match[0]
            # Capture value from any quote type or unquoted string
            value = match[1] or match[2] or match[3]
            if not value:
                continue

            if "{{" in value:
                # Handle dynamic strings: "/user/{{ id }}" -> "/user/" ~ (id)
                expr = re.sub(r'\{\{\s*(.*?)\s*\}\}', r'" ~ (\1) ~ "', value)
                # Clean up empty string concatenations
                expr = f'"{expr}"'.replace('"" ~ ', '').replace(' ~ ""', '')
                pairs.append(f'{key}={expr}')
            else:
                # Static string
                pairs.append(f'{key}="{value}"')
                
        return ", ".join(pairs)

class TemplateParser:
    """
    Parses Nexy templates. 
    1. Removes ALL comments (HTML & Jinja2) from the entire document.
    2. Converts PascalCase tags (<User />) to Jinja2 syntax.
    """

    # Robust Regex for comments with re.DOTALL to handle multiple lines
    _HTML_COMMENT_RE = re.compile(r'', re.DOTALL)
    _JINJA_COMMENT_RE = re.compile(r'\{#.*?#\}', re.DOTALL)
    
    # PascalCase components detection
    _SELF_CLOSING_RE = re.compile(r'<([A-Z]\w*)\s*([^>]*?)\s*/>')
    _BLOCK_RE = re.compile(r'<([A-Z]\w*)\s*([^>]*?)>(.*?)</\1>', re.DOTALL)

    def __init__(self) -> None:
        self.known_components: Set[str] = set()

    def parse(self, html: str, known_components: Optional[Set[str]] = None) -> str:
        # STEP 1: GLOBAL COMMENT STRIPPING
        # This removes comments everywhere, including inside <header> or <ul>
        content = self._HTML_COMMENT_RE.sub('', html)
        content = self._JINJA_COMMENT_RE.sub('', content).strip()
        
        if known_components:
            self.known_components.update(known_components)

        # STEP 2: PASCALCASE TAG VALIDATION
        # Ensure tags like <Image /> are actually imported/known
        used_tags = set(re.findall(r'<([A-Z][a-zA-Z0-9_]*)', content))
        if self.known_components:
            unknowns = used_tags - self.known_components
            unknowns.remove("Slot") if "Slot" in unknowns else None  # Slot is a reserved component
            if  unknowns :
                raise NexyParserError(f"Missing Import: <{list(unknowns)[0]}> used but not declared.")
        
        # STEP 3: PASCALCASE TRANSFORMATIONS
        
        # Self-closing: <User name="Loém" /> -> {{ User(name="Loém") }}
        content = self._SELF_CLOSING_RE.sub(self._replace_self_closing, content)

        # Blocks: <Layout>...</Layout> -> {% call Layout() %}...{% endcall %}
        # Loop handles nested components within each other
        prev_content = None
        while content != prev_content:
            prev_content = content
            content = self._BLOCK_RE.sub(self._replace_block, content)
        
        return content

    def _replace_self_closing(self, match: re.Match[str]) -> str:
        tag, attrs = match.group(1), match.group(2)
        formatted_attrs = TemplateFormatter.format_attributes(attrs)
        return f'{{{{ {tag}({formatted_attrs}) }}}}'

    def _replace_block(self, match: re.Match[str]) -> str:
        tag, attrs, inner_html = match.group(1), match.group(2), match.group(3)
        formatted_attrs = TemplateFormatter.format_attributes(attrs)
        return f'{{% call {tag}({formatted_attrs}) %}}{inner_html}{{% endcall %}}'