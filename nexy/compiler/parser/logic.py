import ast
from typing import List, Optional, cast

from nexy.core.models import (
    LogicResult,
    NexyImport,
    NexyProp,
    ComponentType,
)
from .sanitizer import LogicSanitizer

class ASTUtils:
    """Helper class to reduce the complexity of AST inspection."""
    
    @staticmethod
    def is_prop_annotation(node: ast.AnnAssign) -> bool:
        """Checks if the node is a prop annotation: var: prop[T]"""
        return (isinstance(node.annotation, ast.Subscript) and 
                isinstance(node.annotation.value, ast.Name) and 
                node.annotation.value.id == "prop")

    @staticmethod
    def extract_loader_args(node: ast.Assign) -> Optional[dict]: # type: ignore
        """Attempts to extract path/framework/symbol from a __nexy_loader__ or __Import call."""
        if not (isinstance(node.value, ast.Call)): return None
        
        call = node.value
        func = call.func

        # Accept multiple loader call patterns:
        # 1) __nexy_loader__.import_component(...)
        # 2) __Import(...)
        valid_call = False
        if isinstance(func, ast.Attribute):
            if (isinstance(func.value, ast.Name) and 
                    func.value.id == "__nexy_loader__" and 
                    func.attr == "import_component"):
                valid_call = True
        elif isinstance(func, ast.Name):
            if func.id == "__Import":
                valid_call = True

        if not valid_call:
            return None

        # Simple extraction of keyword arguments
        args = {}
        for kw in call.keywords:
            if isinstance(kw.value, ast.Constant):
                args[kw.arg] = kw.value.value
        return args # type: ignore


class LogicParser:
    """
    Parser for the logic block of a Nexy component.
    Uses an AST-based approach after sanitization to extract props and component imports.
    """
    def __init__(self) -> None:
        self.sanitizer = LogicSanitizer()


    def process(self, code: str, current_file: str) -> LogicResult:
        """
        Processes the logic block code and returns a LogicResult containing 
        extracted props, imports, and the cleaned Python code.
        """
        result = LogicResult()
        if not code.strip():
            return result

        # 1. Pre-processing
        clean_code = self.sanitizer.sanitize(code, current_file=current_file)
        
        # 2. AST Analysis
        try:
            tree = ast.parse(clean_code)
        except SyntaxError as e:
            # Re-raise with a clear message for the user
            raise SyntaxError(f"Logic Parse Error: {e}")

        # 3. Data Extraction & Final Code Construction
        final_body = self._process_nodes(tree.body, result)
        
        if final_body:
            result.python_code = self._wrap_in_module(final_body)

        return result

    def _process_nodes(self, nodes: List[ast.stmt], result: LogicResult) -> List[ast.stmt]:
        """Iterates through AST nodes to extract metadata and filter nodes."""
        final_nodes = []
        for node in nodes:
            # Case A: Props
            if isinstance(node, ast.AnnAssign) and ASTUtils.is_prop_annotation(node):
                result.props.append(self._build_prop(node))
                # Skip prop annotations in the final function body
                continue

            # Case B: Component Imports (Variable Assignment from __Import)
            if isinstance(node, ast.Assign):
                if self._try_extract_import(node, result):
                    final_nodes.append(node) # type: ignore
                    continue

            # Case C: Standard Python code
            final_nodes.append(node) # type: ignore
            
        return final_nodes # type: ignore

    def _wrap_in_module(self, nodes: List[ast.stmt]) -> str:
        """Unparses the filtered nodes back into a Python source string."""
        full_module = ast.Module(
            body=nodes,
            type_ignores=[]
        )
        return ast.unparse(full_module)

    def _build_prop(self, node: ast.AnnAssign) -> NexyProp:
        """Builds a NexyProp object from an AnnAssign node."""
        ann = cast(ast.Subscript, node.annotation)
        target = cast(ast.Name, node.target)
        
        return NexyProp(
            name=target.id,
            type=ast.unparse(ann.slice),
            default=ast.unparse(node.value) if node.value else None
        )

    def _try_extract_import(self, node: ast.Assign, result: LogicResult) -> bool:
        """Attempts to extract import metadata for the component manifest."""
        args = ASTUtils.extract_loader_args(node) # type: ignore
        if not args:
            return False

        target = node.targets[0]
        alias = target.id if isinstance(target, ast.Name) else None
        
        path = args.get("path") # type: ignore
        symbol = args.get("symbol") # type: ignore
        fw_str = args.get("framework") # type: ignore

        if not path or not symbol: 
            return False

        # If it's a CSS import, collect it
        if fw_str == "css" or (path and path.endswith(".css")):
            result.css_imports.append(path)

        # Determine the component type based on extension or framework hint
        comp_type = self._determine_component_type(path, fw_str) # type: ignore
        ext = path[path.rfind("."):] if "." in path else "" # type: ignore

        result.nexy_imports.append(NexyImport(
            path=path, # type: ignore
            symbol=symbol, # type: ignore
            alias=alias,
            raw_source="",
            extension=ext, # type: ignore
            comp_type=comp_type
        ))
        return True

    def _determine_component_type(self, path: str, framework: Optional[str]) -> ComponentType:
        """Maps file extensions and framework strings to ComponentType."""
        path_lower = path.lower()
        mapping = {
            ".nexy": ComponentType.NEXY,
            ".vue": ComponentType.VUE,
            ".svelte": ComponentType.SVELTE,
            ".tsx": ComponentType.REACT,
            ".jsx": ComponentType.REACT,
            ".json": ComponentType.JSON
        }
        
        # 1. Priority to file extension
        for ext, ctype in mapping.items():
            if path_lower.endswith(ext):
                return ctype
                
        # 2. Fallback to framework argument hint
        fw_map = {
            "vue": ComponentType.VUE,
            "react": ComponentType.REACT,
            "svelte": ComponentType.SVELTE,
            "json": ComponentType.JSON
        }
        if framework in fw_map:
            return fw_map[framework]
            
        return ComponentType.UNKNOWN
