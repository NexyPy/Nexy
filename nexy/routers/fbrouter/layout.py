from pathlib import Path
from typing import Optional
from nexy.core.config import Config
from nexy.core.string import StringTransform

class RouteLayout:
    @staticmethod
    def get_closest_import(source_path: str, is_layout: bool = False) -> Optional[str]:
        try:
            path = Path(source_path).resolve()
            root = Path(Config.ROUTER_PATH).resolve()
            
            current = path.parent.parent if is_layout else path.parent
            current = current.resolve()
            limit_dir = root.parent 

            while str(current).startswith(str(limit_dir)):
                layout_candidate = current / "layout.nexy"
                
                if layout_candidate.is_file() and layout_candidate != path:
                    try:
                        # 1. Get the relative path as a POSIX string (with slashes)
                        rel_path = layout_candidate.relative_to(Path.cwd())
                        raw_path = rel_path.as_posix()
                    except ValueError:
                        raw_path = layout_candidate.as_posix()

                    # 2. Normalize the path while slashes still exist
                    # This ensures (article) becomes article_ngp
                    normalized_path = StringTransform.normalize_route_path_for_namespace(raw_path)
                    
                    # 3. Strip extension and convert to Python module dots
                    module_path = normalized_path.rsplit(".", 1)[0].replace("/", ".")
                    
                    # 4. Apply namespace
                    namespace = getattr(Config, "NAMESPACE", "__nexy__.").replace("/", ".")
                    if not namespace.endswith("."):
                        namespace += "."
                        
                    return f"{namespace}{module_path}"

                if current == limit_dir:
                    break
                current = current.parent

        except Exception:
            return None
            
        return None