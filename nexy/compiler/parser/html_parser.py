from html.parser import HTMLParser

from nexy.compiler.parser.nodes import ElementNode, Node, TextNode


class NexyHTMLParser(HTMLParser):
    """Parses Nexy template HTML into an AST."""

    def __init__(self) -> None:
        super().__init__()
        self.root: list[Node] = []
        self.stack: list[ElementNode] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handles the start of a tag, preserving case for Nexy components."""
        raw_tag_text = self.get_starttag_text()
        is_self_closing = False
        attr_dict = {}

        if raw_tag_text:
            import re

            # 1. Extract Tag Name (preserving case)
            # Match the first word after '<'
            tag_match = re.search(r"<([a-zA-Z0-9_:.-]+)", raw_tag_text)
            if tag_match:
                tag = tag_match.group(1)

            # 2. Extract Attributes (preserving case)
            # This regex handles: attr="val", attr='val', attr=val, and valueless attr
            # It also handles spaces around '='
            attr_pattern = re.compile(
                r"(?P<name>[a-zA-Z0-9_:.-]+)"  # Attribute name
                r"(?:\s*=\s*"  # Optional = with spaces
                r'(?:"(?P<v1>[^"]*)"|'  # Double quoted value
                r"'(?P<v2>[^']*)'|"  # Single quoted value
                r"(?P<v3>[^\s/>]+)))?",  # Unquoted value
                re.IGNORECASE,
            )

            # Start searching after the tag name
            search_pos = tag_match.end() if tag_match else 0
            for m in attr_pattern.finditer(raw_tag_text, search_pos):
                attr_name = m.group("name")
                # Value is in one of the three groups
                attr_value = m.group("v1") or m.group("v2") or m.group("v3") or ""
                attr_dict[attr_name] = attr_value

            # 3. Check for Self-Closing
            if raw_tag_text.strip().endswith("/>"):
                is_self_closing = True

        # Fallback if regex failed
        if not attr_dict and attrs:
            attr_dict = {k: (v if v is not None else "") for k, v in attrs}

        node = ElementNode(tag_name=tag, attributes=attr_dict, is_self_closing=is_self_closing)

        if self.stack:
            self.stack[-1].children.append(node)
        else:
            self.root.append(node)

        # Void elements in HTML
        void_elements = {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }

        # RULE: Lowercase tags follow HTML void rules.
        # Uppercase tags (Components) ALWAYS allow children.
        is_component = tag and tag[0].isupper()
        is_void_html = tag.lower() in void_elements

        is_void = is_void_html and not is_component

        if not is_self_closing and not is_void:
            self.stack.append(node)
        else:
            node.is_self_closing = True

    def handle_endtag(self, tag: str) -> None:
        tag_lower = tag.lower()
        # Search for the matching start tag in the stack (from top to bottom)
        # This handles cases where some tags might have been closed implicitly
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i].tag_name.lower() == tag_lower:
                # Close all tags above this one
                while len(self.stack) > i:
                    self.stack.pop()
                break

    def handle_data(self, data: str) -> None:
        if not data:
            return

        node = TextNode(content=data)
        if self.stack:
            self.stack[-1].children.append(node)
        else:
            self.root.append(node)

    def parse(self, html: str) -> list[Node]:
        self.root = []
        self.stack = []
        self.feed(html)
        return self.root
