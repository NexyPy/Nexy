import shutil
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class TemplateRenderer:
    """Copies a local template directory and renders .jinja2 files with context.

    Supports suffix-based filtering: files ending with .react, .vue, .svelte,
    .solid, .preact are only included when client_framework matches.
    The suffix is stripped from the destination filename.

    Bare .jinja2 files (no extension before .jinja2) get the framework-appropriate
    extension appended via FW_EXT_MAP so that a single file can produce
    .nexy / .vue / .svelte / .tsx output depending on client_framework.
    """

    FW_SUFFIXES = {".react", ".vue", ".svelte", ".solid", ".preact", ".none"}
    FILTER_SUFFIXES = FW_SUFFIXES

    FW_EXT_MAP = {
        "none": ".nexy",
        "vue": ".vue",
        "svelte": ".svelte",
        "react": ".tsx",
        "preact": ".tsx",
        "solid": ".tsx",
    }

    def __init__(self, src: Path, dest: Path, context: dict | None = None):
        self.src = src
        self.dest = dest
        self.context = context or {}

    def render(self) -> None:
        if not self.src.is_dir():
            raise FileNotFoundError(f"Template directory not found: {self.src}")

        env = Environment(loader=FileSystemLoader(str(self.src)))
        self.dest.mkdir(parents=True, exist_ok=True)

        for src_path in self.src.rglob("*"):
            rel = src_path.relative_to(self.src)

            if src_path.is_dir():
                continue

            target_rel = self._resolve_target(rel)
            if target_rel is None:
                continue

            is_jinja2 = target_rel.suffix == ".jinja2"
            dest_path = self.dest / str(target_rel)

            if is_jinja2:
                template = env.get_template(rel.as_posix())
                output = template.render(**self.context)
                dest_stem = dest_path.with_suffix("")
                if not output.strip():
                    continue
                dest_stem.parent.mkdir(parents=True, exist_ok=True)
                dest_stem.write_text(output, encoding="utf-8")
            else:
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_path, dest_path)

        # Clean up empty directories left after filtering
        for dir_path in sorted(self.dest.rglob("*"), key=lambda p: len(str(p)), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                dir_path.rmdir()

    def _resolve_target(self, rel: Path) -> Path | None:
        name = rel.name
        parts = name.split(".")

        has_jinja2 = parts[-1] == "jinja2"
        if has_jinja2:
            parts.pop()

        name_stripped = ".".join(parts)

        fw_map = {
            ".react": "react",
            ".vue": "vue",
            ".svelte": "svelte",
            ".solid": "solid",
            ".preact": "preact",
            ".none": "none",
        }
        matched = False
        skip = False

        while len(parts) > 1:
            suffix = "." + parts[-1]
            if suffix not in self.FILTER_SUFFIXES:
                break
            parts.pop()

            expected = fw_map.get(suffix)
            actual = self.context.get("client_framework", "")
            if expected is None or expected != actual.lower():
                skip = True
                continue

            matched = True

        if not matched and any(name_stripped.endswith(s) for s in self.FW_SUFFIXES):
            skip = True

        if skip:
            return None

        target = ".".join(parts)

        if has_jinja2:
            # FW_EXT_MAP replaces the suffix when a FW_SUFFIX was matched,
            # or adds an extension for bare .jinja2 filenames
            if matched or "." not in target:
                fw = self.context.get("client_framework", "")
                fw_ext = self.FW_EXT_MAP.get(fw.lower())
                if fw_ext:
                    target += fw_ext
            target += ".jinja2"

        return rel.parent / target
