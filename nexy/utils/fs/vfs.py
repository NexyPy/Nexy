import os
from pathlib import Path


class VFS:
    """
    In-memory Virtual File System.
    Singleton class to store compiled files during runtime.
    """

    _instance = None
    _files: dict[str, str] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def write(self, path: str, content: str) -> None:
        """Writes content to a virtual file path."""
        path = path.replace("\\", "/")
        self._files[path] = content

    def read(self, path: str) -> str:
        """Reads content from a virtual file path."""
        path = path.replace("\\", "/")
        if path not in self._files:
            raise FileNotFoundError(f"Virtual file not found: {path}")
        return self._files[path]

    def exists(self, path: str) -> bool:
        """Checks if a virtual file exists."""
        path = path.replace("\\", "/")
        return path in self._files

    def list_files(self) -> list[str]:
        """Returns a list of all files in the VFS."""
        return list(self._files.keys())

    def clear(self) -> None:
        """Clears all files from the VFS."""
        self._files.clear()

    def delete(self, path: str) -> None:
        """Deletes a file from the VFS."""
        path = path.replace("\\", "/")
        if path in self._files:
            del self._files[path]

    def flush_to_disk(self, prefix: str = "__nexy__") -> None:
        """Writes all VFS files under prefix to the physical filesystem."""
        for path, content in self._files.items():
            if not path.startswith(prefix):
                continue
            disk_path = Path(path)
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            disk_path.write_text(content, encoding="utf-8")
