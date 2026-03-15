import os
import re
import pathlib
from typing import Match, List, Optional
from nexy.core.config import Config

class LogicSanitizer:
    """
    Sanitizer for Nexy logic blocks.
    Handles custom import syntaxes like 'from "./file.nexy" import Comp' 
    or 'import "./data.json" as data' and converts them to valid Python code.
    """
    def __init__(self):
        self.aliases = Config.ALIASES
        self.namespace = Config.NAMESPACE
        
        # Regex for: from "path" import targets
        self.RE_NEXY_FROM = re.compile(
            r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import\s+(?P<targets>.+?)(?=\n\S|$)', 
            re.M | re.S
        )
        
        # Regex for: import "path" [as alias]
        self.RE_NEXY_IMPORT = re.compile(
            r'^\s*import\s+["\'](?P<path>[^"\']+)["\'](?:\s+as\s+(?P<alias>\w+))?(?=\n\S|$)',
            re.M | re.S
        )

    def _resolve_full_path(self, current_file: str, import_str: str) -> str:
        """
        Resolves the full relative path from the current file, 
        taking aliases and relative paths into account.
        """
        is_relative = import_str.startswith("./") or import_str.startswith("../")
        is_alias = any(import_str.startswith(alias) for alias in self.aliases)

        if not (is_relative or is_alias):
            return import_str  # Standard module or external

        root_path = pathlib.Path.cwd().absolute()
        current_path = pathlib.Path(current_file).absolute()

        # 1. Handle Aliases
        for alias, replacement in self.aliases.items():
            if import_str.startswith(alias):
                resolved_path = root_path / import_str.replace(alias, replacement.strip("/"), 1)
                return resolved_path.absolute().relative_to(root_path).as_posix()

        # 2. Handle Relative Paths (./ and ../)
        resolved_path = current_path.parent.joinpath(import_str).resolve()

        try:
            return resolved_path.relative_to(root_path).as_posix()
        except ValueError:
            # Fallback if path is outside project root
            return os.path.normpath(resolved_path).replace("\\", "/")

    def _clean_targets(self, targets_str: str) -> List[str]:
        """Cleans parentheses, newlines, and spaces from import targets."""
        cleaned = targets_str.replace("(", "").replace(")", "").replace("\n", " ")
        return [t.strip() for t in cleaned.split(",") if t.strip()]

    def _get_framework(self, extension: str) -> str:
        """Returns the framework name associated with the extension."""
        return Config.FRONTEND_EXTENSIONS.get(extension.lower(), 'unknown')

    def sanitize(self, source: str, current_file: str) -> str:
        """
        Main entry point for sanitizing logic blocks.
        Transforms custom Nexy import syntax into valid Python AST-parsable code.
        """
        # 1. Transform 'from "path" import targets'
        source = self.RE_NEXY_FROM.sub(lambda m: self._replace_from(m, current_file), source)
        
        # 2. Transform 'import "path" [as alias]'
        source = self.RE_NEXY_IMPORT.sub(lambda m: self._replace_import(m, current_file), source)
        
        return source

    def _normalize_alias(self, name: str) -> str:
        """Converts a string into a valid Python identifier."""
        # Replace non-alphanumeric characters with underscores
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def _replace_from(self, match: Match, current_file: str) -> str:
        """Callback for 'from "path" import targets' transformation."""
        path_str = match.group("path")
        targets_raw = match.group("targets")
        
        full_rel_path = self._resolve_full_path(current_file, path_str)
        ext = pathlib.Path(full_rel_path).suffix.lower()
        targets = self._clean_targets(targets_raw)

        # --- LOGIC (Nexy / Python) ---
        if ext in ('.nexy', '.py') or ext == '':
            is_nexy = ext == '.nexy'
            prefix = f"{self.namespace.replace('/', '.')}" if is_nexy else ""
            module_name = re.sub(r'\.nexy$|\.py$', '', full_rel_path)
            module_name = re.sub(r'\.+', '.', module_name.replace("/", ".")).strip(".")
            module_name = prefix + module_name
            return f"from {module_name} import {', '.join(targets)}"

        # --- RUNTIME (TSX, JSX, VUE, SVELTE, JSON, etc.) ---
        framework = self._get_framework(ext)
        
        import_lines = []
        for t in targets:
            parts = re.split(r'\s+as\s+', t, flags=re.I)
            symbol = parts[0]
            alias = parts[1] if len(parts) > 1 else symbol
            alias = self._normalize_alias(alias)
            
            line = (f'{alias} = __Import('
                    f'path="{full_rel_path}", framework="{framework}", symbol="{symbol}")')
            import_lines.append(line)

        return "\n".join(import_lines)

    def _replace_import(self, match: Match, current_file: str) -> str:
        """Callback for 'import "path" [as alias]' transformation."""
        path_str = match.group("path")
        alias = match.group("alias")
        
        full_rel_path = self._resolve_full_path(current_file, path_str)
        ext = pathlib.Path(full_rel_path).suffix.lower()
        
        # If no alias provided, use the filename stem as the default alias
        if not alias:
            alias = self._normalize_alias(pathlib.Path(full_rel_path).stem)

        # --- LOGIC (Nexy / Python) ---
        if ext in ('.nexy', '.py') or ext == '':
            is_nexy = ext == '.nexy'
            prefix = f"{self.namespace.replace('/', '.')}" if is_nexy else ""
            module_name = re.sub(r'\.nexy$|\.py$', '', full_rel_path)
            module_name = re.sub(r'\.+', '.', module_name.replace("/", ".")).strip(".")
            module_name = prefix + module_name
            return f"import {module_name} as {alias}"

        # --- RUNTIME (JSON, VUE, etc.) ---
        framework = self._get_framework(ext)
        # For simple imports, we assume 'default' symbol unless specified (not possible in simple import syntax)
        return f'{alias} = __Import(path="{full_rel_path}", framework="{framework}", symbol="default")'
