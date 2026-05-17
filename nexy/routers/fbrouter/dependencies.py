import importlib
import inspect
from pathlib import Path
from typing import Any, Callable, List
from nexy.core.config import Config
from nexy.core.string import StringTransform

class RouteDependencies:
    @staticmethod
    def collect(source_path: str) -> List[Callable[..., Any]]:
        """
        Collects 'dependencies' list from dependencies.py files following 
        the directory hierarchy, exactly like layout.nexy inheritance.
        """
        deps: List[Callable[..., Any]] = []
        try:
            path = Path(source_path).resolve()
            # The root of the router (e.g., src/routes)
            root = Path(Config.ROUTER_PATH).resolve()
            current = path.parent.resolve()

            # 1. Build the chain of directories from current up to root
            chain: List[Path] = []
            # We use root.parent as limit to ensure we can capture dependencies.py at root level
            limit_dir = root.parent 

            while str(current).startswith(str(limit_dir)):
                chain.append(current)
                if current == root or current == limit_dir:
                    break
                current = current.parent

            # 2. Process from Top to Bottom (reversed) to respect inheritance order
            for directory in reversed(chain):
                dep_file = directory / "dependencies.py"
                
                if dep_file.is_file():
                    try:
                        # Get relative path for module resolution
                        
                        rel_path = dep_file.relative_to(Path.cwd())
                        raw_path = rel_path.as_posix()
                        
                        # Normalize path (handle (grouping) folders like layout logic)
                        normalized_path = raw_path.replace(".py","").replace("/", ".")
                        
                        try:
                            mod = importlib.import_module(normalized_path)
                        except Exception as e:
                            print(e)
                        candidates = getattr(mod, "dependencies", None)
                        if isinstance(candidates, (list, tuple)):
                            deps.extend([c for c in candidates if callable(c)])
                            
                    except Exception:
                        continue
                        
        except Exception:
            return deps
        
        return deps