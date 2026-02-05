import re
import pathlib
from typing import Match, List
from nexy.nexyconfig import NexyConfig

class LogicSanitizer:
    def __init__(self):
        self.aliases = NexyConfig.ALIASES
        self.namespace = NexyConfig.NAMESPACE
        # Regex mise à jour : supporte les sauts de ligne et parenthèses via re.DOTALL et groupage
        self.RE_NEXY_FROM = re.compile(
            r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import\s+(?P<targets>.+?)(?=\n\S|$)', 
            re.M | re.S
        )

    def _resolve_full_path(self, current_file: str, import_str: str) -> str:
        current_path = pathlib.Path(current_file)
        
        for alias, replacement in self.aliases.items():
            if import_str.startswith(alias):
                return import_str.replace(alias, replacement.strip("/") + "/", 1).lstrip("/")
        
        target_path = (current_path.parent / import_str)
        try:
            return target_path.resolve().relative_to(pathlib.Path.cwd()).as_posix()
        except ValueError:
            return target_path.as_posix().replace("../", "").replace("./", "")

    def _clean_targets(self, targets_str: str) -> List[str]:
        """Nettoie les parenthèses, sauts de ligne et espaces des cibles d'import."""
        # Enlever les parenthèses et normaliser les espaces
        cleaned = targets_str.replace("(", "").replace(")", "").replace("\n", " ")
        # Découper par virgule et filtrer les vides
        return [t.strip() for t in cleaned.split(",") if t.strip()]

    def sanitize(self, source: str, current_file: str) -> str:
        def _replace_callback(match: Match) -> str:
            path_str = match.group("path")
            targets_raw = match.group("targets")
            
            full_rel_path = self._resolve_full_path(current_file, path_str)
            ext = pathlib.Path(full_rel_path).suffix.lower()
            targets = self._clean_targets(targets_raw)

            # --- LOGIQUE (Nexy / Python) ---
            if ext in ('.nexy', '.py') or ext == '':
                is_nexy = ext == '.nexy'
                module_name = re.sub(r'\.nexy$|\.py$', '', full_rel_path)
                module_name = re.sub(r'\.+', '.', module_name.replace("/", ".")).strip(".")
                
                prefix = f"{self.namespace}." if is_nexy else ""
                # On reconstruit la chaîne des targets proprement
                return f"from {prefix}{module_name} import {', '.join(targets)}"

            # --- RUNTIME (TSX, JSX, VUE, JSON) ---
            framework = {'.tsx': 'react', '.jsx': 'react', '.vue': 'vue'}.get(ext, 'unknown')
            
            import_lines = []
            for t in targets:
                parts = re.split(r'\s+as\s+', t, flags=re.I)
                symbol = parts[0]
                alias = parts[1] if len(parts) > 1 else symbol
                
                line = (f'{alias} = __Import('
                        f'path="{full_rel_path}", framework="{framework}", symbol="{symbol}")')
                import_lines.append(line)

            return "\n".join(import_lines)

        return self.RE_NEXY_FROM.sub(_replace_callback, source)