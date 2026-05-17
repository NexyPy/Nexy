import hashlib
import json
from pathlib import Path
from html import escape as _html_escape
from typing import Any, Dict, Optional
from nexy.core.config import Config

class NCC:
    """Nexy Client Component placeholder generator."""
    
    def __init__(self, path: str, framework: str, symbol: str) -> None:
        self.path = path
        self.framework = framework.lower()
        self.symbol = symbol
        self._seq = 0

    def generate(self, props: Dict[str, Any] , caller: callable = None) -> str:
        self._seq += 1
        mount_id = self._generate_mount_id()
        if caller:
            props["children"] = f"{caller()}"
        props_json = self._serialize_props(props)
        url = self._resolve_path()
        
        return self._render_tag(url, mount_id, props_json)

    def _generate_mount_id(self) -> str:
        base = f"{self.path}|{self.symbol}|{self._seq}"
        h = hashlib.md5(base.encode()).hexdigest()[:10]
        return f"nexy-{h}"

    def _serialize_props(self, props: Dict[str, Any]) -> str:
        try:
            return json.dumps(props)
        except Exception:
            return "{}"

    def _resolve_path(self) -> str:
        aliases = getattr(Config, "ALIASES", {}) or {}
        resolved = self.path
        
        for key, target in aliases.items():
            k = key.rstrip("/")
            if resolved == k or resolved.startswith(f"{k}/"):
                t = target.lstrip("/")
                suffix = resolved[len(k):].lstrip("/")
                resolved = f"/{t}/{suffix}" if suffix else f"/{t}"
                break
        
        if not resolved.startswith("/") and not (resolved.startswith("./") or resolved.startswith("../")):
            stripped = resolved.lstrip("./")
            for base in ["src", "src/components"]:
                candidate = Path(getattr(Config, "PROJECT_ROOT", ".")).joinpath(base, stripped)
                if candidate.is_file():
                    return f"/{candidate.as_posix().lstrip('/')}"
        
        return resolved if resolved.startswith("/") else f"/{resolved}"

    def _render_tag(self, url: str, mount_id: str, props_json: str) -> str:
        esc_props = _html_escape(props_json, quote=True)
        esc_symbol = _html_escape(self.symbol, quote=True)
        esc_fw = _html_escape(self.framework, quote=True)
        esc_url = _html_escape(url, quote=True)
        
        is_prod = Path("__nexy__/nexy.prod").is_file()
        
        # Static content retrieval
        content = self._get_static_content(esc_url, esc_symbol)
        key_hash = hashlib.md5(url.encode("utf-8")).hexdigest()

        path_attr = f'data-nexy-path="{esc_url}" ' if not is_prod else ""
        
        return (
            f'<ncc id="{mount_id}" '
            f'data-nexy-fw="{esc_fw}" '
            f'{path_attr}'
            f'data-nexy-key="{key_hash}" '
            f'style="display: contents;" '
            f'data-nexy-symbol="{esc_symbol}" '
            f'data-nexy-props="{esc_props}">{content}</ncc>'
        )

    def _get_static_content(self, url: str, symbol: str) -> str:
        clean_url = url.replace(".tsx", "")
        if self.framework in ["vue", "svelte"]:
            default_path = Path(f"__nexy__/client/static{url}.html")
        else:
            default_path = Path(f"__nexy__/client/static{clean_url}.Default.html")
            
        export_path = Path(f"__nexy__/client/static{clean_url}.{symbol}.html")

        if export_path.is_file():
            return export_path.read_text(encoding="utf-8")
        if default_path.is_file():
            return default_path.read_text(encoding="utf-8")
        return ""