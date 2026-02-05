import ast
import textwrap
from nexy.core.models import PaserModel


class LogicGenerator:
    def __init__(self) -> str:
        self.func_name :str
        self.source : PaserModel | None = None
        self.output : str
        self.template_path :str
        self.FRONTMATTER : str
    
    def generate(
            self,
            template_path: str,
            source: PaserModel,
            )-> None:
        self.source = source
        
        self.template_path = template_path
        names = template_path.split("/")
        lenght = len(names) - 1
        self.func_name = names[lenght].replace(".md","").replace(".html","")

        self.func_name = self.func_name[0].capitalize() + self.func_name[1:]
        if template_path.endswith(".html"):
            self.output = template_path.replace(".html",".py")
        else :
            self.output = template_path.replace(".md",".py")
        
        self.FRONTMATTER = self._companent_model()
        with open(self.output, "w", encoding="utf-8") as file:
            file.write(self.FRONTMATTER)
            return True

    def _resolve_props(self) -> str:
        props = ""
        endIdx = len(self.source.props) -1
        for prop in self.source.props:
            end = "" if prop == self.source.props[endIdx] else ","
            props += f"{prop.name}: {prop.type} = {prop.default}{end} "
        return props
    def _companent_model(self) -> None:
        LOGIC = self.source.frontmatter
        LOGIC = textwrap.indent(LOGIC, "    ")
        props = self._resolve_props()

        # Build an explicit context dict (no locals()) by collecting
        # prop names and top-level identifiers defined in the frontmatter
        names = []
        try:
            tree = ast.parse(self.source.frontmatter)
            idents = set()
            for node in tree.body:
                # Assign targets
                if isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            idents.add(t.id)
                        elif isinstance(t, ast.Tuple):
                            for el in t.elts:
                                if isinstance(el, ast.Name):
                                    idents.add(el.id)
                # Function and class definitions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    idents.add(node.name)
        except Exception:
            idents = set()

        # Include props (they are function parameters) and collected idents
        prop_names = [p.name for p in self.source.props]
        for n in prop_names:
            idents.add(n)

        # Filter and order for stable output
        names = [n for n in sorted(idents) if not n.startswith('_')]

        context_items = ", ".join([f'"{n}": {n}' for n in names])

        return f"""from typing import *
from fastapi import *
from nexy import Template as __Template , Import as __Import

def {self.func_name}({props}) -> str:
    {'\r'+LOGIC}
    
    context = {{{context_items}}}
    # Template Rendering
    __inner = __Template("{self.template_path}", context)
    # Layout Wrapping
    return __inner
"""

   