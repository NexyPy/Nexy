import ast
import re

import markdown
from nexy.core.config import Config
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
        self.config = Config()

    def _clean_jinja_wrapping(self, html_content: str) -> str:
        # Nettoie les {% ... %}
        content = re.sub(r'<([a-zA-Z0-9]+)>\s*({%.*?%})\s*</\1>', r'\2', html_content)
        # Nettoie les {{ ... }}
        content = re.sub(r'<([a-zA-Z0-9]+)>\s*({{.*?}})\s*</\1>', r'\2', content)
        return content


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
        if current_file.endswith(".mdx"):
            jinja_code = self._clean_jinja_wrapping(jinja_code)
            jinja_code = jinja_code.replace("{%", "<startblock>").replace("%}","</endblock>")
            jinja_code = markdown.markdown(jinja_code, 
                                           extensions=self.config.MARKDOWN_EXTENSIONS,
                                           extension_configs={
                                                "pymdownx.highlight": {

                                                    # IMPORTANT
                                                    "pygments_lang_class": True,

                                                    "linenums": False,
                                                    
                                                }
                                                
                                            },
                                           )
            jinja_code = jinja_code.replace("<startblock>", "{%").replace("</endblock>", "%}")
            jinja_code = jinja_code.replace("<p>{%", "{%").replace("%}</p>", "%}")

        return PaserModel(
            frontmatter=logic_result.python_code,
            template=jinja_code,
            props=logic_result.props,
            context=[],
            styles=logic_result.css_imports,
        )

__all__ = ["Parser"]
