import ast
from nexy.core.models import PaserModel
from .template import TemplateParser
from .scanner import Scanner
from .logic import LogicParser
from .validator import ImportValidator

class Parser:
    def __init__(self) -> None:
        self.scanner = Scanner()
        self.logic_parser = LogicParser()
        self.template_parser = TemplateParser()


    def process(self, source_code: str, current_file: str) -> PaserModel:
        # 1. Découpage
        blocks = self.scanner.scan(source_code)

        # 2. Analyse de la logique (Python)
        logic_result = self.logic_parser.process(blocks.logic_block, current_file=current_file)
        
        # 2.5. Validation des imports
        ImportValidator.validate_imports(logic_result.nexy_imports, current_file)

        # 3. Préparation des composants connus pour le template
        # On extrait les alias ou les noms de symboles des imports Nexy
        known_components: set[str] = set()
        for imp in logic_result.nexy_imports:
            # Si on a 'import X as Y', on cherche 'Y' dans le template
            name = imp.alias if imp.alias else imp.symbol
            if name:
                known_components.add(name)

        if logic_result.python_code:
            
            try:
                tree = ast.parse(logic_result.python_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom):
                        for alias in node.names:
                            name = alias.asname or alias.name
                            if name and name[0].isupper():
                                known_components.add(name)
            except SyntaxError:
                pass

        jinja_code = self.template_parser.parse(blocks.template_block, known_components=known_components)

        return PaserModel(
            frontmatter=logic_result.python_code,
            template=jinja_code,
            props=logic_result.props,
            context=[None],
        )

__all__ = ["Parser"]