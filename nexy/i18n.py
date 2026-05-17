import json
import os
import locale as _py_locale
from pathlib import Path
from functools import lru_cache
from typing import Any

FALLBACK_LOCALE = "en"

def _normalize(tag: str) -> str:
    t = (tag or "").lower().replace("_", "-")
    if t.startswith("fr"): return "fr"
    if t.startswith("hi") or t.startswith("in"): return "hi"
    if t.startswith("zh"): return "zh"
    if t.startswith("en"): return "en"
    return FALLBACK_LOCALE

@lru_cache(maxsize=1)
def _detect_locale() -> str:
    for env in ("LC_ALL", "LC_MESSAGES", "LANG"):
        v = os.environ.get(env)
        if v: return _normalize(v)
    try:
        loc = _py_locale.getdefaultlocale()[0]
        if loc: return _normalize(loc)
    except Exception:
        pass
    try:
        loc = _py_locale.getlocale()[0]
        if loc: return _normalize(loc)
    except Exception:
        pass
    return FALLBACK_LOCALE

def _deep_merge(base: dict[str, Any], other: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for k, v in other.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out

@lru_cache(maxsize=8)
def _load_locale(locale: str) -> dict[str, Any]:
    root = Path(__file__).parent / "i18n"
    data: dict[str, Any] = {}
    flat = root / f"{locale}.json"
    if flat.exists():
        with flat.open("r", encoding="utf-8") as f:
            data = json.load(f)
    modular_dir = root / locale
    if modular_dir.is_dir():
        for pack in sorted(modular_dir.glob("*.json")):
            try:
                with pack.open("r", encoding="utf-8") as f:
                    data = _deep_merge(data, json.load(f))
            except Exception:
                continue
    return data

def t(key: str, default: str | None = None, *, locale: str | None = None) -> str:
    loc = locale or _detect_locale()
    data = _load_locale(loc) or _load_locale(FALLBACK_LOCALE)
    value: Any = data
    for part in key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default if default is not None else key
    if isinstance(value, str):
        return value
    return default if default is not None else key
