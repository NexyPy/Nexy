import os
import sys
from typing import Optional

from nexy.core.models import NexyConfigModel

_current_dir = os.getcwd()
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)


class Config(NexyConfigModel):
    _instance: Optional["Config"] = None
    _load_error: str | None = None

    ALIASES: dict[str, str] = {}
    NAMESPACE: str = "__nexy__/"
    MARKDOWN_EXTENSIONS: list[str] = [
        "extra",
        "tables",
        "fenced_code",
        "codehilite",
        "toc",
        "admonition",
        "attr_list",
        "pymdownx.highlight",
        "pymdownx.superfences",
        "pymdownx.inlinehilite",
        "pymdownx.details",
        "pymdownx.tabbed",
    ]
    TARGET_EXTENSIONS: list[str] = [".nexy", ".mdx"]
    FF_REGISTRY: dict[str, object] = {}
    ROUTE_FILE_EXTENSIONS: list[str] = [".nexy", ".mdx", ".py"]
    ROUTE_FILE_EXCEPTIONS: list[str] = ["__init__.py", "layout.nexy", "dependencies.py"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy", "index.mdx"]
    PROJECT_ROOT: str = "."
    ROUTER_PATH: str = "src/routes"
    WATCH_EXTENSIONS_GLOB: list[str] = ["*.py", "*.mdx", "*.nexy"]
    WATCH_EXCLUDE_PATTERNS: list[str] = [
        "*/.git/*",
        "*/.venv/*",
        "*/__nexy__/*",
        "*/__pycache__/*",
        "*/venv/*",
        "*/node_modules/*",
        "*.tmp",
    ]
    FRONTEND_EXTENSIONS: dict[str, str] = {
        ".tsx": "react",
        ".jsx": "react",
        ".vue": "vue",
        ".svelte": "svelte",
        ".solid": "solid",
        ".preact": "preact",
        ".json": "json",
        ".css": "css",
    }

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self) -> None:
        if self._loaded:
            return
        self._loaded = True
        self._load()
        if Config._load_error is not None:
            self._loaded = False

    def _load(self) -> None:
        try:
            import nexyconfig
        except ModuleNotFoundError:
            Config._load_error = "nexyconfig.py not found"
            return
        except SyntaxError as e:
            Config._load_error = f"nexyconfig.py has a syntax error: {e}"
            return
        except Exception as e:
            Config._load_error = f"nexyconfig.py failed to load: {e}"
            import traceback as _tb
            _tb.print_exc()
            return

        nc = nexyconfig.NexyConfig

        for attr in NexyConfigModel.__annotations__:
            val = getattr(nc, attr, None)
            if val is not None:
                setattr(Config, attr, val)

        if Config.useAliases:
            Config.ALIASES = Config.useAliases

        if Config.useMarkdownExtensions:
            Config.MARKDOWN_EXTENSIONS = Config.useMarkdownExtensions

        watch_ext = getattr(nc, "useWatchExtensions", None)
        if watch_ext:
            Config.WATCH_EXTENSIONS_GLOB = watch_ext

        watch_exclude = getattr(nc, "useWatchExcludePatterns", None)
        if watch_exclude:
            Config.WATCH_EXCLUDE_PATTERNS = watch_exclude

        ff_list = Config.useFF
        if ff_list:
            mapping: dict[str, str] = dict(Config.FRONTEND_EXTENSIONS)
            registry: dict[str, object] = {}
            for ff in ff_list:
                name = getattr(ff, "name", None)
                exts = getattr(ff, "extension", []) or []
                if name:
                    registry[name.lower()] = ff
                    for ext in exts:
                        e = ext if ext.startswith(".") else f".{ext}"
                        mapping[e.lower()] = name.lower()
            Config.FRONTEND_EXTENSIONS = mapping
            Config.FF_REGISTRY = registry

        Config.WATCH_EXTENSIONS_GLOB = [f"*{ext}" for ext in Config.ROUTE_FILE_EXTENSIONS]
        Config._load_error = None
