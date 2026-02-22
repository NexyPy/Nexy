import hashlib
import json
import base64
import mimetypes
from pathlib import Path
from html import escape as _html_escape
from typing import Any, Callable, Dict
from nexy.core.config import Config


class Import:
    def __new__(cls, path: str, framework: str, symbol: str) -> Callable[..., str]:
        ext = Path(path).suffix.lower()

        # Cas 1 : JSON → valeur Python directement exploitable dans le frontmatter / template
        if ext == ".json":
            try:
                p = Path(path)
                if not p.is_absolute():
                    p = Path(Config.PROJECT_ROOT).joinpath(path)
                with p.open("r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

        # Cas 2 : image → data URL base64
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            try:
                p = Path(path)
                if not p.is_absolute():
                    p = Path(Config.PROJECT_ROOT).joinpath(path)
                data = p.read_bytes()
                mime, _ = mimetypes.guess_type(str(p))
                if not mime:
                    mime = "application/octet-stream"
                b64 = base64.b64encode(data).decode("ascii")
                return f"data:{mime};base64,{b64}"
            except Exception:
                return ""

        # Cas 3 : composant frontend → placeholder HTML
        return _Importer(path=path, framework=framework, symbol=symbol)


class _Importer:
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.path = path
        self.framework = framework.lower()
        self.symbol = symbol
        self._seq = 0

    def __call__(self, **kwargs: Any) -> str:
        self._seq += 1
        mount_id = self._mount_id(self.path, self.symbol, self._seq)
        props = self._serialize_props(kwargs)
        return self._placeholder(self.framework, self.path, mount_id, props)

    def _mount_id(self, path: str, symbol: str, seq: int) -> str:
        base = f"{path}|{symbol}|{seq}"
        h = hashlib.md5(base.encode()).hexdigest()[:10]
        return f"nexy-{h}"

    def _serialize_props(self, props: Dict[str, Any]) -> str:
        try:
            return json.dumps(props)
        except Exception:
            return "{}"

    def _placeholder(self, framework: str, path: str, mount_id: str, props_json: str) -> str:
        aliases = getattr(Config, "ALIASES", {}) or {}
        resolved = path
        for key, target in aliases.items():
            k = key.rstrip("/")
            if resolved == k or resolved.startswith(f"{k}/"):
                t = target.lstrip("/")
                suffix = resolved[len(k):].lstrip("/")
                resolved = f"/{t}/{suffix}" if suffix else f"/{t}"
                break
        if not resolved.startswith("/"):
            if resolved.startswith("./") or resolved.startswith("../") or not any(resolved.startswith(prefix) for prefix in aliases.keys()):
                stripped = resolved
                while stripped.startswith("./"):
                    stripped = stripped[2:]
                while stripped.startswith("../"):
                    stripped = stripped[3:]
                candidates = ["src", "src/components"]
                for base in candidates:
                    from pathlib import Path as _P
                    candidate_path = _P(getattr(Config, "PROJECT_ROOT", ".")).joinpath(base, stripped)
                    if candidate_path.is_file():
                        resolved = f"/{candidate_path.as_posix().lstrip('/')}"
                        break
        url = resolved if resolved.startswith("/") else f"/{resolved}"
        esc_props = _html_escape(props_json, quote=True)
        esc_symbol = _html_escape(self.symbol, quote=True)
        esc_fw = _html_escape(framework, quote=True)
        esc_url = _html_escape(url, quote=True)
        return (
            f'<div id="{mount_id}" '
            f'data-nexy-fw="{esc_fw}" '
            f'data-nexy-path="{esc_url}" '
            f'data-nexy-symbol="{esc_symbol}" '
            f'data-nexy-props="{esc_props}"></div>'
        )
