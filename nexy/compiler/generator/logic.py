import ast
import textwrap
import re
from pathlib import Path
from typing import *
from nexy.core.models import ParserModel, NexyProp
from nexy.core.string import StringTransform
from nexy.routers.fbrouter.layout import RouteLayout


class LogicGenerator:
    def __init__(self) -> None:
        self.func_name: str = ""
        self.source: ParserModel | None = None
        self.output: str = ""
        self.template_path: str = ""
        self.FRONTMATTER: str = ""
        self._string_transform = StringTransform()
        self.source_path: str = None
    
    def generate(self, template_path: str, source: ParserModel, source_path:str = None) -> None:
        self.source = source
        self.source_path = source_path
        self.template_path = template_path
        names = template_path.split("/")
        stem = names[-1].replace(".md", "").replace(".html", "")
        raw_name = self._string_transform.get_component_name(stem)
        
        self.func_name = re.sub(r'[^a-zA-Z0-9_]', '_', raw_name)
        
        if template_path.endswith(".html"):
            self.output = template_path.replace(".html", ".py")
        else:
            self.output = template_path.replace(".md", ".py")

        self.FRONTMATTER = self._component_model()
        with open(self.output, "w", encoding="utf-8") as file:
            file.write(self.FRONTMATTER)

    def _resolve_props(self) -> str:
        assert self.source is not None
        if not self.source.props:
            return ""
        return ", ".join([f"{p.name}: {p.type} = {p.default}" for p in self.source.props])

    def _component_model(self) -> str:
        assert self.source is not None
        LOGIC = textwrap.indent(self.source.frontmatter, "    ")
        props = self._resolve_props()
    
        is_layout_file = self.source_path.endswith("layout.nexy")
        layout_import = RouteLayout.get_closest_import(self.source_path, is_layout=is_layout_file)
        
        layout_header = ""
        render_wrapper = "rendered"
        layout_children = ""
        
        if layout_import:
            layout_header = f"from {layout_import} import Layout as __Layout\n"
            render_wrapper = "str(__Layout(children=rendered))"
        # -----------------------

        if is_layout_file :
            layout_children = f"""children = f"<nslot  style='display:contents;'>{"{children}"}</nslot>" """

        # Extraction des identifiants Python (AST)
        idents = set()
        try:
            tree = ast.parse(self.source.frontmatter)
            for node in tree.body:
                if isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name != '*':
                            idents.add(alias.asname if alias.asname else alias.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        idents.add(alias.asname if alias.asname else alias.name.split('.')[0])
                elif isinstance(node, ast.Assign):
                    for t in node.targets:
                        if isinstance(t, ast.Name): idents.add(t.id)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    idents.add(node.name)
        except: pass

        for p in self.source.props: idents.add(p.name)
        names = [n for n in sorted(idents) if not n.startswith('_')]
        
        context_items = ", ".join([f'"{n}": {n}' for n in names])
        Slot = ""
        if "src/routes/" not in self.source_path:
            Slot = "Slot = caller if caller else lambda: ''"
            context_items = context_items + ", 'Slot':Slot" if context_items != "" else "'Slot':Slot"   
            props = props+ ", caller:Union[callable, None] = None" if props != "" else "caller:Union[callable, None] = None"

        # Gestion CSS
        css_blocks = []
        for css_path in self.source.styles:
            p = Path(css_path)
            if p.exists():
                css_blocks.append(f"<style>\n{p.read_text(encoding='utf-8')}\n</style>")
        css_injection = "\n".join(css_blocks)

        return f"""from typing import *
from fastapi import *
from pathlib import Path as __Path
from nexy import Template as __Template , Import as __Import
from jinja2 import Template as __JinjaTemplate
NexyElement = Union[callable, __JinjaTemplate]
{layout_header}
def {self.func_name}({props}) -> str:
    {Slot}
{LOGIC}
    {layout_children}
    context = {{{context_items}}}
    rendered = str(__Template().render("{self.template_path}", context))
    styles = \"\"\"{css_injection}\"\"\"
    
    # Rendu final (potentiellement enveloppé par le Layout)
    return {render_wrapper} + styles
"""
    
