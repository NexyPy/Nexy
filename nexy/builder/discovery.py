import traceback
from collections.abc import Generator
from pathlib import Path

from nexy.core.config import Config


class Discovery:
    """Scanner de fichiers pour trouver les fichiers .nexy et .mdx."""

    TARGET_EXTENSIONS = Config.TARGET_EXTENSIONS
    DEFAULT_EXCLUDED_DIRS = {
        "__pycache__",
        ".git",
        ".venv",
        "node_modules",
        "dist",
        "build",
        "__nexy__",
    }

    def __init__(self) -> None:
        # On initialise avec une copie des exclusions par défaut
        self.excluded_dirs = self.DEFAULT_EXCLUDED_DIRS.copy()

    def scan(self, root_path: Path | str) -> list[Path]:
        """Scanne le répertoire racine de manière récursive."""
        root = Path(root_path)
        if not root.is_dir():
            raise FileNotFoundError(f"Le répertoire {root} n'existe pas ou n'est pas un dossier")

        return list(self._walk(root))

    def _walk(self, current_path: Path) -> Generator[Path, None, None]:
        """Générateur interne pour parcourir l'arborescence."""
        try:
            for item in current_path.iterdir():
                if item.is_dir():
                    if item.name not in self.excluded_dirs:
                        yield from self._walk(item)
                elif item.suffix in self.TARGET_EXTENSIONS:
                    yield item
        except PermissionError:
            traceback.print_exc()

    def add_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.add(dir_name)

    def remove_excluded_dir(self, dir_name: str) -> None:
        self.excluded_dirs.discard(dir_name)


# discovery = Discovery()

# # 2. Lance le scan
# files = discovery.scan(".")
# for f in files:
#     print(str(f))
