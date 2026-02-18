import re
from typing import Optional


class Pathname:
    def __init__(self, pathname: str) -> None:
        self.pathname = "/" + pathname.strip("/")

    def _dynamic_pathname(self, path: Optional[str] = None) -> str:
        """Transforme [slug] en {slug}."""
        target = path or self.pathname
        # Regex: cherche ce qui est entre crochets, sauf si ça commence par '...'
        return re.sub(r'\[(?!(\.\.\.))([^\]]+)\]', r'{\2}', target)

    def _catch_all(self, path: Optional[str] = None) -> str:
        """Transforme [...slug] en {slug:path}."""
        target = path or self.pathname
        return re.sub(r'\[\.\.\.([^\]]+)\]', r'{\1:path}', target)

    def _group_pathname(self, path: Optional[str] = None) -> str:
        """Supprime les segments entre parenthèses comme /(user)/."""
        target = path or self.pathname
        # Supprime /(group) et gère les doubles slashes résultants
        cleaned = re.sub(r'/\([^)]+\)', '', target)
        return cleaned if cleaned else "/"

    def _normalize_pathname(self, path: str = None) -> str:
        target = path or self.pathname
        # Next.js : /docs/index -> /docs et /index -> /
        if target.endswith("/index"):
            target = target[:-6] # Retire "/index"
        return target if target else "/"


    def process(self) -> str:
        """Exécute toutes les transformations dans l'ordre logique."""
        res = self._group_pathname()
        res = self._normalize_pathname(res)
        res = self._catch_all(res)
        res = self._dynamic_pathname(res)
        
        # Nettoyage final des slashes doubles
        res = re.sub(r'/+', '/', res)
        return res if (res == "/" or not res.endswith("/")) else res.rstrip("/")



class StringTransform:
    def __init__(self) -> None:
        pass

    @staticmethod
    def resolve_pathname(pathname: str) -> str:
        return pathname.replace("/", "")

    @staticmethod
    def _normalize_dynamic_segment(segment: str) -> str:
        if segment.startswith("[...") and segment.endswith("]"):
            name = segment[4:-1]
            return f"{name}_ndp"
        if segment.startswith("[") and segment.endswith("]"):
            name = segment[1:-1]
            return f"{name}_ndp"
        if segment.startswith("(") and segment.endswith(")"):
            name = segment[1:-1]
            return f"{name}_ngp"
        return segment

    @staticmethod
    def normalize_route_path_for_namespace(path: str) -> str:
        parts = path.split("/")
        if not parts:
            return path
        *dirs, filename = parts
        normalized_dirs = [StringTransform._normalize_dynamic_segment(p) for p in dirs]
        if "." in filename:
            stem, ext = filename.rsplit(".", 1)
            original = stem
            has_dynamic = "[" in stem and "]" in stem
            if has_dynamic:
                stem = re.sub(r'\[\.\.\.([^\]]+)\]', r'\1', stem)
                stem = re.sub(r'\[([^\]]+)\]', r'\1', stem)
                stem = stem.replace("-", "_")
                stem = f"{stem}_ndc"
            filename = f"{stem}.{ext}"
        normalized_parts = [p for p in normalized_dirs if p] + [filename]
        return "/".join(normalized_parts)

    def get_component_name(self, pathname: str) -> str:
        segment = pathname.split("/")[-1]
        if "[" in segment and "]" in segment:
            cleaned = re.sub(r'\[\.\.\.([^\]]+)\]', r'\1', segment)
            cleaned = re.sub(r'\[([^\]]+)\]', r'\1', cleaned)
            cleaned = cleaned.replace("-", "_")
            if not cleaned:
                return ""
            first = cleaned[0].capitalize()
            return f"{first}{cleaned[1:]}_ndc"
        if not segment:
            return ""
        first_letter = segment[0].capitalize()
        return first_letter + segment[1:]
    
    

class ComponentString :
    def __init__(self ,pathname: str): 
        self.pathname = pathname

    def get_name(self) -> str:
        component_name = self.pathname.split("/")[-1]
        first_letter = component_name[0].capitalize()
        component_name = first_letter + component_name[1:]
        return component_name
