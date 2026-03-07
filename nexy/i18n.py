import json
from pathlib import Path
from functools import lru_cache
from typing import Any

_DEFAULT_LOCALE = "en"

@lru_cache(maxsize=4)
def _load_locale(locale: str) -> dict[str, Any]:
    base = Path(__file__).parent / "i18n" / f"{locale}.json"
    if base.exists():
        with base.open("r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def t(key: str, default: str | None = None, *, locale: str | None = None) -> str:
    loc = locale or _DEFAULT_LOCALE
    data = _load_locale(loc)
    value = data
    for part in key.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            return default if default is not None else key
    if isinstance(value, str):
        return value
    return default if default is not None else key

