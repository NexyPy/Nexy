from pathlib import Path


class PathUtil:
    """
    Consolidated path utilities for files and folders.
    Replaces old File, Folder, and PathName classes.
    """

    @staticmethod
    def normalize(name: str) -> str:
        """Normalizes a string for use in pathnames (lowercase, no spaces)."""
        return name.replace(" ", "_").lower()

    @staticmethod
    def read_file(path: str | Path) -> str:
        """Reads content from a file."""
        return Path(path).read_text(encoding="utf-8")

    @staticmethod
    def write_file(path: str | Path, content: str) -> None:
        """Writes content to a file."""
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")

    @staticmethod
    def exists(path: str | Path) -> bool:
        """Checks if a path exists."""
        return Path(path).exists()

    @staticmethod
    def delete(path: str | Path) -> bool:
        """Deletes a file or directory."""
        p = Path(path)
        if not p.exists():
            return False

        if p.is_file():
            p.unlink()
        else:
            p.rmdir()
        return True

    @staticmethod
    def ensure_dir(path: str | Path) -> None:
        """Ensures a directory exists."""
        Path(path).mkdir(parents=True, exist_ok=True)
