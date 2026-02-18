import os
import sys
import traceback

from nexy.core.models import NexyConfigModel


current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from nexyconfig import NexyConfig
except ImportError as e:
    traceback.print_exc()
    print(f"Error importing nexyconfig: {e.with_traceback(None)}")


class Config:
    ALIASES: dict[str, str] = {}
    NAMESPACE: str = "__nexy__/"
    MARKDOWN_EXTENSIONS: list[str] = ["extra", "codehilite"]
    TARGET_EXTENSIONS: list[str] = [".nexy", ".mdx"]
    ROUTE_FILE_EXTENSIONS: list[str] = [".nexy", ".mdx", ".py"]
    ROUTE_FILE_EXCEPTIONS: list[str] = ["__init__.py", "layout.nexy"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy", "index.mdx"]
    PROJECT_ROOT: str = "."
    ROUTER_PATH: str = "src/routes"
    useRouter: object | None = None
    nexy_config: NexyConfigModel | None = None

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
        except Exception as e:
            self.nexy_config = None
            # traceback.print_exc()
            # print(f"Error loading nexyconfig: {e.with_traceback(traceback.format_exc())}")
