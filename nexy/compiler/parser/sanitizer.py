import os
import re
import pathlib
from typing import Match, List
from nexy.core.config import Config

class LogicSanitizer:
    def __init__(self):
        self.aliases = Config.ALIASES
        self.namespace = Config.NAMESPACE
        # Regex mise à jour : supporte les sauts de ligne et parenthèses via re.DOTALL et groupage
        self.RE_NEXY_FROM = re.compile(
            r'^\s*from\s+["\'](?P<path>[^"\']+)["\']\s+import\s+(?P<targets>.+?)(?=\n\S|$)', 
            re.M | re.S
        )

    def _resolve_full_path(self, current_file: str, import_str: str) -> str:
        # 1. On vérifie si c'est un import local ou un alias
        # Si ça ne commence pas par ., .. ou un alias, on retourne l'import tel quel
        is_relative = import_str.startswith("./") or import_str.startswith("../")
        is_alias = any(import_str.startswith(alias) for alias in self.aliases)

        if not (is_relative or is_alias):
            return import_str  # C'est un module externe ou standard

        root_path = pathlib.Path.cwd().absolute()
        current_path = pathlib.Path(current_file).absolute()

        # 2. Gestion des Alias
        for alias, replacement in self.aliases.items():
            if import_str.startswith(alias):
                resolved_path = root_path / import_str.replace(alias, replacement.strip("/"), 1)
                return resolved_path.absolute().relative_to(root_path).as_posix()

        # 3. Gestion des chemins relatifs (./ et ../)
        # .normpath ou .resolve() nettoient les segments ../
        resolved_path = current_path.parent.joinpath(import_str).resolve()

        try:
            return resolved_path.relative_to(root_path).as_posix()
        except ValueError:
            # Si on sort du projet, on renvoie le chemin nettoyé mais brut
            return os.path.normpath(resolved_path).replace("\\", "/")
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
                prefix = f"{self.namespace.replace("/",".")}" if is_nexy else ""
                module_name = re.sub(r'\.nexy$|\.py$', '', full_rel_path)
                module_name = re.sub(r'\.+', '.', module_name.replace("/", ".")).strip(".")
                module_name = prefix + module_name
                # On reconstruit la chaîne des targets proprement
                return f"from {module_name} import {', '.join(targets)}"

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
