import pathlib
from typing import List
from nexy.core.models import NexyImport
from nexy.core.config import Config


class ImportValidationError(Exception):
    """Raised when an imported path cannot be resolved.

    The message includes the original import, the resolved path and
    optional suggestions (files with same stem) to help the user fix it.
    """
    pass


class ImportValidator:
    """Validates that all imported files exist on the filesystem and
    raises helpful, precise errors when they don't.
    """

    @staticmethod
    def _find_suggestions(path: pathlib.Path) -> List[str]:
        """Return filenames in the same directory that share the same stem."""
        parent = path.parent
        if not parent.exists():
            return []
        stem = path.stem
        candidates = []
        for p in parent.iterdir():
            if p.is_file() and p.stem == stem:
                candidates.append(p.name)
        return candidates

    @staticmethod
    def validate_imports(imports: List[NexyImport], current_file: str) -> None:
        """
        Check that all imported files exist.

        Raises ImportValidationError with a helpful message when an import
        path cannot be resolved. The message contains:
        - original import path
        - symbol/alias (if provided)
        - resolved absolute path
        - optional filename suggestions
        """
        # Work with absolute paths to avoid duplicate segments
        current_dir = pathlib.Path(current_file).resolve().parent
        project_root = pathlib.Path(getattr(Config, "PROJECT_ROOT", ".")).resolve()

        for imp in imports:
            raw = imp.path.replace("\\", "/")
            import_path = pathlib.Path(imp.path)

            # Determine base resolution:
            # - Absolute paths: keep as-is
            # - Explicit relative ("./" or "../"): resolve from current file's directory
            # - Project-relative (e.g., "src/..."): resolve from project root to avoid duplications
            if import_path.is_absolute():
                full_path = import_path.resolve()
            elif raw.startswith("./") or raw.startswith("../"):
                full_path = (current_dir / import_path).resolve()
            else:
                full_path = (project_root / import_path).resolve()

            if full_path.exists():
                continue

            suggestions = ImportValidator._find_suggestions(full_path)

            parts = [f"Missing import file: '{imp.path}'"]
            if imp.symbol:
                parts.append(f"symbol='{imp.symbol}'")
            if imp.alias:
                parts.append(f"alias='{imp.alias}'")
            parts.append(f"resolved='{full_path}'")

            # Raise a concise, user-friendly error with context
            hint = f" suggestions={suggestions}" if suggestions else ""
            raise ImportValidationError(
                f'Import Error "{imp.path}" does not exist; {", ".join(parts)}{hint}'
            )


__all__ = ["ImportValidator", "ImportValidationError"]
