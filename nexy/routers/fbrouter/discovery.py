from pathlib import Path
from typing import List
from nexy.core.config import Config

class RouteDiscovery:
    def __init__(self) -> None:
        self.config = Config()
        self.router_path = Path(self.config.ROUTER_PATH)

    def scan(self) -> List[Path]:
        """Scan the directory recursively and return valid route files."""
        if not self.router_path.is_dir():
            raise FileNotFoundError(f"Directory {self.router_path} not found")

        # Optimized scanning using rglob and centralized validation
        return [
            path for path in self.router_path.rglob("*")
            if self._is_valid_route(path)
        ]

    def _is_valid_route(self, path: Path) -> bool:
        """Centralized validation logic for file-based routing."""
        # Check if it's a file with allowed extensions and not in exceptions
        if not path.is_file() or \
           path.suffix not in self.config.ROUTE_FILE_EXTENSIONS or \
           path.name in self.config.ROUTE_FILE_EXCEPTIONS:
            return False

        # Ignore files or directories starting with '_'
        # relative_to ensures we only check segments within the router directory
        relative_parts = path.relative_to(self.router_path).parts
        if any(part.startswith("_") for part in relative_parts):
            return False

        return True