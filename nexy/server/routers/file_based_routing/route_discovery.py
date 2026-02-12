import importlib
from pathlib import Path
from nexy.nexyconfig import NexyConfig


class RouteDiscovery:
        def __init__(self) -> None:
            self.config = NexyConfig()
            self.router_path = self.config.ROUTER_PATH

        def scan(self) -> None:
            """Scanne le répertoire racine de manière récursive ."""
            root = Path(self.router_path)
            if not root.is_dir():
                raise FileNotFoundError(f"Le répertoire {root} n'existe pas ou n'est pas un dossier")
            
            # print(f"Scanning for route files in: {list(self._walk(root))}")
            return list(self._walk(root))
        def _walk(self, current_path: Path):
            """Générateur interne pour parcourir l'arborescence."""
            try:
                for item in current_path.iterdir():
                    if item.is_dir():
                            yield from self._walk(item)
                    elif item.suffix in self.config.ROUTE_FILE_EXTENSIONS:
                        yield item
            except PermissionError:
                pass
