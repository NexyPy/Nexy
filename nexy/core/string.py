import re


class Pathname:
    def __init__(self, pathname: str) -> None:
        self.pathname = "/" + pathname.strip("/")

    def _dynamic_pathname(self, path: str | None = None) -> str:
        """Convert [slug] to {slug}."""
        target = path or self.pathname
        # Regex: find content inside brackets, unless it starts with '...'
        return re.sub(r"\[(?!(\.\.\.))([^\]]+)\]", r"{\2}", target)

    def _catch_all(self, path: str | None = None) -> str:
        """Convert [...slug] to {slug:path}."""
        target = path or self.pathname
        return re.sub(r"\[\.\.\.([^\]]+)\]", r"{\1:path}", target)

    def _group_pathname(self, path: str | None = None) -> str:
        """Remove parenthesized segments like /(user)/."""
        target = path or self.pathname
        # Remove /(group) and handle resulting double slashes
        cleaned = re.sub(r"/\([^)]+\)", "", target)
        return cleaned if cleaned else "/"

    def _normalize_pathname(self, path: str | None = None) -> str:
        target = path or self.pathname
        # Next.js: /docs/index -> /docs and /index -> /
        if target.endswith("/index"):
            target = target[:-6]  # Remove "/index"
        return target if target else "/"

    def process(self) -> str:
        """Execute all transformations in logical order."""
        res = self._group_pathname()
        res = self._normalize_pathname(res)
        res = self._catch_all(res)
        res = self._dynamic_pathname(res)

        # Final cleanup of double slashes
        res = re.sub(r"/+", "/", res)
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
            return f"{segment[4:-1]}_ndp"
        if segment.startswith("[") and segment.endswith("]"):
            return f"{segment[1:-1]}_ndp"
        if segment.startswith("(") and segment.endswith(")"):
            return f"{segment[1:-1]}_ngp"
        return segment

    @staticmethod
    def normalize_route_path_for_namespace(path: str) -> str:
        path = path.strip("/")
        if not path:
            return ""

        parts = path.split("/")

        # Case 1: Path points to a directory (no extension in the last segment)
        if "." not in parts[-1]:
            return "/".join([StringTransform._normalize_dynamic_segment(p) for p in parts])

        # Case 2: Path points to a file
        *dirs, filename = parts
        normalized_dirs = [StringTransform._normalize_dynamic_segment(p) for p in dirs]

        stem, ext = filename.rsplit(".", 1)
        if "[" in stem and "]" in stem:
            stem = re.sub(r"\[\.\.\.([^\]]+)\]", r"\1", stem)
            stem = re.sub(r"\[([^\]]+)\]", r"\1", stem)
            stem = stem.replace("-", "_")
            stem = f"{stem}_ndc"

        normalized_parts = [p for p in normalized_dirs if p] + [f"{stem}.{ext}"]
        return "/".join(normalized_parts)

    def get_component_name(self, pathname: str) -> str:
        segment = pathname.split("/")[-1]
        if "[" in segment and "]" in segment:
            cleaned = re.sub(r"\[\.\.\.([^\]]+)\]", r"\1", segment)
            cleaned = re.sub(r"\[([^\]]+)\]", r"\1", cleaned)
            cleaned = cleaned.replace("-", "_")
            if not cleaned:
                return ""
            first = cleaned[0].capitalize()
            return f"{first}{cleaned[1:]}_ndc"
        if not segment:
            return ""
        first_letter = segment[0].capitalize()
        return first_letter + segment[1:]
