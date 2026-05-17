import re

from nexy.compiler.parser.html_parser import NexyHTMLParser
from nexy.compiler.parser.nodes import ElementNode, Node, TextNode


class NexyParserError(Exception):
    """Custom exception for Nexy template parsing errors."""

    pass


class TemplateFormatter:
    """Helper class to format HTML-style attributes into Python/Jinja arguments."""

    # Matches key = "value" with optional spaces around the '='
    _ATTR_REGEX = re.compile(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|(\S+))')

    @classmethod
    def format_dict(cls, attrs: dict[str, str]) -> str:
        if not attrs:
            return ""

        pairs = []
        for key, value in attrs.items():
            # 1. Handle Shorthand or Spread in the key
            # e.g. <Component {{ title }} /> or <Component {{ ...props }} />
            if "{{" in key and (not value or value == ""):
                inner_match = re.search(r"\{\{\s*(.*?)\s*\}\}", key)
                if inner_match:
                    inner = inner_match.group(1).strip()
                    if inner.startswith("...") or inner.startswith("**"):
                        # Spread: {{ ...props }} -> **props
                        var_name = inner.lstrip(".*").strip()
                        pairs.append(f"**{var_name}")
                        continue
                    elif " " not in inner and "(" not in inner:
                        # Shorthand: {{ title }} -> title=title
                        pairs.append(f"{inner}={inner}")
                        continue
                    else:
                        # Raw expression injection: {{ "class='foo'" }}
                        # For components, this is unusual but we can support it if it returns a dict
                        # But Jinja2 macros expect keyword args.
                        pass

            # 2. Handle dynamic values
            if "{{" in value:
                # Handle dynamic strings: "/user/{{ id }}" -> "/user/" ~ (id)
                # If the entire value is just a Jinja expression: {{ user.name }}
                if (
                    value.strip().startswith("{{")
                    and value.strip().endswith("}}")
                    and value.count("{{") == 1
                ):
                    inner_match = re.search(r"\{\{\s*(.*?)\s*\}\}", value)
                    if inner_match:
                        expr = inner_match.group(1).strip()
                        pairs.append(f"{key}=({expr})")
                        continue

                expr = re.sub(r"\{\{\s*(.*?)\s*\}\}", r'" ~ (\1) ~ "', value)
                # Clean up empty string concatenations
                expr = f'"{expr}"'.replace('"" ~ ', "").replace(' ~ ""', "")
                pairs.append(f"{key}={expr}")
            elif cls._is_unquoted_value(value):
                # Unquoted value: count=5, price=9.99, active=true
                pairs.append(f"{key}={value}")
            else:
                # Quoted string
                pairs.append(f'{key}="{value}"')

        return ", ".join(pairs)

    @classmethod
    def _is_unquoted_value(cls, value: str) -> bool:
        """Determines if a value should be rendered without quotes in Jinja2."""
        if not value:
            return False

        # Booleans and None
        if value.lower() in ("true", "false", "none"):
            return True

        # Numbers (integers and floats, including negative ones)
        try:
            float(value)
            return True
        except ValueError:
            pass

        return False


class TemplateParser:
    """
    Parses Nexy templates using an AST-based approach with a protection layer for Jinja2 blocks.
    1. Protects Jinja2 blocks to prevent HTMLParser from mangling them.
    2. Removes ALL comments.
    3. Converts PascalCase tags (<User />) to Jinja2 syntax.
    """

    # Robust Regex for comments with re.DOTALL to handle multiple lines
    _HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
    _JINJA_COMMENT_RE = re.compile(r"\{#.*?#\}", re.DOTALL)

    # Jinja2 blocks protection regex
    _JINJA_BLOCK_RE = re.compile(r"\{\{.*?\}\}|\{%.*?%\}|\{#.*?#\}", re.DOTALL)

    def __init__(self) -> None:
        self.known_components: set[str] = set()
        self.parser = NexyHTMLParser()
        self.placeholders: list[str] = []

    def _protect_jinja(self, html: str) -> str:
        self.placeholders = []

        def replace(match):
            placeholder = f"NXYPJ{len(self.placeholders)}Z"
            self.placeholders.append(match.group(0))
            return placeholder

        return self._JINJA_BLOCK_RE.sub(replace, html)

    def _unprotect_jinja(self, html: str) -> str:
        for i, original in enumerate(self.placeholders):
            html = html.replace(f"NXYPJ{i}Z", original)
        return html

    def parse(self, html: str, known_components: set[str] | None = None) -> str:
        # STEP 1: GLOBAL COMMENT STRIPPING
        content = self._HTML_COMMENT_RE.sub("", html)
        content = self._JINJA_COMMENT_RE.sub("", content).strip()

        # STEP 2: PROTECT JINJA2 BLOCKS
        content = self._protect_jinja(content)

        if known_components:
            self.known_components.update(known_components)

        # STEP 3: PARSE TO AST
        nodes = self.parser.parse(content)

        # STEP 4: VALIDATE COMPONENTS
        self._validate_components(nodes)

        # STEP 5: RENDER AST TO JINJA2
        jinja_template = self._render_nodes(nodes)

        # STEP 6: UNPROTECT JINJA2 BLOCKS
        return self._unprotect_jinja(jinja_template)

    def _validate_components(self, nodes: list[Node]) -> None:
        for node in nodes:
            if isinstance(node, ElementNode):
                if node.is_component():
                    tag_name = self._unprotect_jinja(node.tag_name)
                    if tag_name not in self.known_components and tag_name != "Slot":
                        raise NexyParserError(
                            f"Missing Import: <{tag_name}> used but not declared."
                        )
                self._validate_components(node.children)

    def _render_nodes(self, nodes: list[Node]) -> str:
        return "".join(self._render_node(node) for node in nodes)

    def _render_node(self, node: Node) -> str:
        if isinstance(node, TextNode):
            return node.content

        if isinstance(node, ElementNode):
            if node.is_component():
                return self._render_component(node)
            else:
                return self._render_element(node)

        return ""

    def _render_component(self, node: ElementNode) -> str:
        # For components, we must unprotect BOTH keys and values before formatting
        unprotected_attrs = {
            self._unprotect_jinja(k): self._unprotect_jinja(v) for k, v in node.attributes.items()
        }
        formatted_attrs = TemplateFormatter.format_dict(unprotected_attrs)

        tag_name = self._unprotect_jinja(node.tag_name)

        if node.is_self_closing and not node.children:
            return f"{{{{ {tag_name}({formatted_attrs}) }}}}"
        else:
            children_content = self._render_nodes(node.children)
            return f"{{% call {tag_name}({formatted_attrs}) %}}{children_content}{{% endcall %}}"

    def _render_element(self, node: ElementNode) -> str:
        attrs_str = ""
        if node.attributes:
            pairs = []
            for k, v in node.attributes.items():
                # Handle dynamic attribute injection: <div {{ "class='foo'" }}>
                if "{{" in k and (not v or v == ""):
                    pairs.append(self._unprotect_jinja(k))
                    continue

                if v:
                    # We keep placeholders here, they will be unprotected in the final step
                    safe_v = v.replace('"', "&quot;")
                    pairs.append(f'{k}="{safe_v}"')
                else:
                    pairs.append(k)

            if pairs:
                attrs_str = " " + " ".join(pairs)

        if node.is_self_closing:
            return f"<{node.tag_name}{attrs_str} />"
        else:
            children_content = self._render_nodes(node.children)
            return f"<{node.tag_name}{attrs_str}>{children_content}</{node.tag_name}>"
