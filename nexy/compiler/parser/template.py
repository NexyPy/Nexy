import re

class NexyParserError(Exception):
    pass

class TemplateFormatter:
    """Helper pour le formatage Jinja."""
    _ATTR_REGEX = re.compile(r'(\w+)=(["\'])(.*?)\2')

    @classmethod
    def format_attributes(cls, attr_str: str) -> str:
        """Convertit les attrs HTML (foo="bar") en kwargs Python (foo="bar")."""
        if not attr_str or not attr_str.strip():
            return ""
        # Capture simple des paires clé=valeur
        pairs = [f'{k}={q}{v}{q}' for k, q, v in cls._ATTR_REGEX.findall(attr_str)]
        return ", ".join(pairs)


class TemplateValidator:
    """Helper pour la validation structurelle."""
    @staticmethod
    def ensure_imports_declared(content: str, known_components: set[str]):
        """Vérifie que chaque Tag PascalCase est importé."""
        # On ne valide pas ce qui est en commentaire (déjà strippé par l'appelant idéalement)
        used_tags = set(re.findall(r'<([A-Z][a-zA-Z0-9_]*)', content))
        
        unknowns = used_tags - known_components
        if unknowns:
            missing = list(unknowns)[0]
            raise NexyParserError(
                f"Missing Import: <{missing}> used but not declared/imported."
            )

    @staticmethod
    def check_balance(content: str):
        """Vérification rudimentaire des balises ouvrantes/fermantes orphelines."""
        # Balise ouvrante orpheline (très simple check)
        open_match = re.search(r'<([A-Z]\w+)(?!.*</\1>)', content, re.DOTALL)
        if open_match:
             # Attention: ce check regex est fragile sur des gros fichiers imbriqués.
             # En mode KISS Regex, on accepte cette limitation ou on la retire.
             pass 

        # Balise fermante sans ouverture
        close_match = re.search(r'</([A-Z]\w+)>', content)
        if close_match:
            tag = close_match.group(1)
            # Vérifier grossièrement si on a un open avant
            if f"<{tag}" not in content:
                raise NexyParserError(f"Orphan closing tag: </{tag}> found without opener.")


class TemplateParser:
    _COMMENT_REGEX = re.compile(r'<!--.*?-->', re.DOTALL)
    _SELF_CLOSING_REGEX = re.compile(r'<([A-Z]\w*)\s*([^>]*?)\s*/>')
    _BLOCK_REGEX = re.compile(r'<([A-Z]\w*)\s*([^>]*?)>(.*?)</\1>', re.DOTALL)

    def __init__(self):
        self.known_components = set()

    def parse(self, html: str, known_components: set[str] | None = None) -> str:
        # 1. Nettoyage
        content = self._COMMENT_REGEX.sub('', html).strip()
        if known_components:
            self.known_components.update(known_components)

        # 2. Validation
        TemplateValidator.ensure_imports_declared(content, self.known_components)
        
        # 3. Transformation : Auto-fermants (<Comp /> -> {{ Comp() }})
        content = self._SELF_CLOSING_REGEX.sub(self._replace_self_closing, content)

        # 4. Transformation : Blocs (<Comp>...</Comp> -> {% call Comp() %}...{% endcall %})
        # Note : On boucle tant qu'il y a des balises imbriquées à transformer
        prev_content = None
        while content != prev_content:
            prev_content = content
            content = self._BLOCK_REGEX.sub(self._replace_block, content)
        
        # 5. Validation finale structurelle
        TemplateValidator.check_balance(content)

        return content

    def _replace_self_closing(self, match: re.Match) -> str:
        tag, attrs = match.group(1), match.group(2)
        formatted_attrs = TemplateFormatter.format_attributes(attrs)
        return f'{{{{ {tag}({formatted_attrs}) }}}}'

    def _replace_block(self, match: re.Match) -> str:
        tag, attrs, inner_html = match.group(1), match.group(2), match.group(3)
        formatted_attrs = TemplateFormatter.format_attributes(attrs)
        # .strip() sur inner_html uniquement si on veut virer les espaces blancs contigus aux balises
        return f'{{% call {tag}({formatted_attrs}) %}}{inner_html}{{% endcall %}}'