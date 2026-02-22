import os
import sys
import traceback

from nexy.core.models import NexyConfigModel


current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

class Config:
    ALIASES: dict[str, str] = {}
    NAMESPACE: str = "__nexy__/"
    MARKDOWN_EXTENSIONS: list[str] = ["extra", "codehilite"]
    TARGET_EXTENSIONS: list[str] = [".nexy", ".mdx"]
    FF_REGISTRY: dict[str, object] = {}
    ROUTE_FILE_EXTENSIONS: list[str] = [".nexy", ".mdx", ".py"]
    ROUTE_FILE_EXCEPTIONS: list[str] = ["__init__.py", "layout.nexy"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy", "index.mdx"]
    PROJECT_ROOT: str = "."
    ROUTER_PATH: str = "src/routes"
    useRouter: object | None = None
    nexy_config: NexyConfigModel | None = None
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
    }

    def __init__(self) -> None:
        self._get_config()

    def _get_config(self) -> None:
        try:
            from nexyconfig import NexyConfig

            nexy_config: NexyConfigModel = NexyConfig()
            self.nexy_config = nexy_config

            for name in dir(nexy_config):
                if name.startswith("_"):
                    continue
                value = getattr(nexy_config, name)
                if callable(value):
                    continue
                setattr(self, name, value)

            aliases = getattr(nexy_config, "useAliases", None)
            if aliases is not None:
                self.ALIASES = aliases
                Config.ALIASES = aliases

            router = getattr(nexy_config, "useRouter", None)
            if router is not None:
                self.useRouter = router
                Config.useRouter = router

            markdown_extensions = getattr(nexy_config, "useMarkdownExtensions", None)
            if markdown_extensions:
                self.MARKDOWN_EXTENSIONS = markdown_extensions
                Config.MARKDOWN_EXTENSIONS = markdown_extensions
            
            watch_ext = getattr(nexy_config, "useWatchExtensions", None)
            if watch_ext:
                self.WATCH_EXTENSIONS_GLOB = watch_ext
                Config.WATCH_EXTENSIONS_GLOB = watch_ext
            
            watch_exclude = getattr(nexy_config, "useWatchExcludePatterns", None)
            if watch_exclude:
                self.WATCH_EXCLUDE_PATTERNS = watch_exclude
                Config.WATCH_EXCLUDE_PATTERNS = watch_exclude
            
            ff_list = getattr(nexy_config, "useFF", None)
            if ff_list:
                mapping: dict[str, str] = dict(Config.FRONTEND_EXTENSIONS)
                registry: dict[str, object] = {}
                for ff in ff_list:
                    try:
                        name = getattr(ff, "name", None)
                        exts = getattr(ff, "extension", []) or []
                        registry[name.lower()] = ff
                        if not name:
                            continue
                        for ext in exts:
                            e = ext if ext.startswith(".") else f".{ext}"
                            mapping[e.lower()] = name.lower()
                    except Exception:
                        continue
                self.FRONTEND_EXTENSIONS = mapping
                Config.FRONTEND_EXTENSIONS = mapping
                self.FF_REGISTRY = registry
                Config.FF_REGISTRY = registry
        except Exception as e:
            self.nexy_config = None
            # traceback.print_exc()
            # print(f"Error loading nexyconfig: {e.with_traceback(traceback.format_exc())}")

        # Aligne les extensions de watcher sur les extensions de routes
        self.WATCH_EXTENSIONS_GLOB = [f"*{ext}" for ext in self.ROUTE_FILE_EXTENSIONS]
        Config.WATCH_EXTENSIONS_GLOB = self.WATCH_EXTENSIONS_GLOB
