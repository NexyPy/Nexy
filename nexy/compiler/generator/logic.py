import ast
import textwrap
from nexy.core.models import PaserModel
from nexy.core.string import StringTransform


class LogicGenerator:
    def __init__(self) -> None:
        self.func_name: str = ""
        self.source: PaserModel | None = None
        self.output: str = ""
        self.template_path: str = ""
        self.FRONTMATTER: str = ""
        self._string_transform = StringTransform()
    
    def generate(
            self,
            template_path: str,
            source: PaserModel,
            )-> None:
        self.source = source
        
        self.template_path = template_path
        names = template_path.split("/")
        length = len(names) - 1
        stem = names[length].replace(".md", "").replace(".html", "")
        self.func_name = self._string_transform.get_component_name(stem)
        if template_path.endswith(".html"):
            self.output = template_path.replace(".html",".py")
        else :
            self.output = template_path.replace(".md",".py")
        
        self.FRONTMATTER = self._component_model()
        with open(self.output, "w", encoding="utf-8") as file:
            file.write(self.FRONTMATTER)

    def _resolve_props(self) -> str:
        if not self.source.props:
            return ""
        parts = [f"{p.name}: {p.type} = {p.default}" for p in self.source.props]
        return ", ".join(parts)

    def _component_model(self) -> str:
        LOGIC = self.source.frontmatter
        LOGIC = textwrap.indent(LOGIC, "    ")
        props = self._resolve_props()
        is_layout = self.template_path.endswith("layout.html") or self.template_path.endswith("layout.md")

        # Build an explicit context dict (no locals()) by collecting
        # prop names, top-level identifiers, AND imported names
        # Handles all Python import cases: simple, aliases, wildcards, relative, etc.
        names = []
        try:
            tree = ast.parse(self.source.frontmatter)
            idents = set()
            for node in tree.body:
                # Handle all import types
                if isinstance(node, ast.ImportFrom):
                    # from module import name [as alias]
                    # from . import module
                    # from .. import module
                    # from module import *
                    for alias in node.names:
                        if alias.name == '*':
                            # Wildcard import: from module import *
                            # Can't determine names, skip
                            continue
                        # Use alias if present, otherwise use imported name
                        imported_name = alias.asname if alias.asname else alias.name
                        # Handle dotted names (from x.y.z import name -> name)
                        if '.' in imported_name:
                            imported_name = imported_name.split('.')[-1]
                        if imported_name and not imported_name.startswith('_'):
                            idents.add(imported_name)
                
                elif isinstance(node, ast.Import):
                    # import module [as alias]
                    # import module1, module2 [as a1, a2]
                    # import .relative
                    # import ..relative
                    for alias in node.names:
                        # Use alias if present, otherwise use first part of module name
                        imported_name = alias.asname if alias.asname else alias.name
                        # For 'import a.b.c' -> use 'a' unless aliased
                        if '.' in imported_name and not alias.asname:
                            imported_name = imported_name.split('.')[0]
                        if imported_name and not imported_name.startswith('_'):
                            idents.add(imported_name)
                
                # Assign targets
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name):
                            idents.add(t.id)
                        elif isinstance(t, ast.Tuple):
                            for el in t.elts:
                                if isinstance(el, ast.Name):
                                    idents.add(el.id)
                
                # Function and class definitions
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
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
from pathlib import Path as __Path
from nexy import Template as __Template , Import as __Import
from jinja2 import Template as __JinjaTemplate
NexyElement = Union[callable, __JinjaTemplate]

def {self.func_name}({props}) -> str:
    {'\r'+LOGIC}
    
    context = {{{context_items}}}
    return str(__Template().render("{self.template_path}", context))
"""

   
