import os
import sys

current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


class Config:
    ALIASES = {"@": "src/components"}
    NAMESPACE = "__nexy__/"
    MARKDOWN_EXTENSIONS = ["extra", "codehilite"]
    TARGET_EXTENSIONS = [".nexy", ".mdx"]
    ROUTE_FILE_EXTENSIONS = [".nexy", ".mdx", ".py"]
    ROUTE_FILE_EXCEPTIONS = ["__init__.py", "layout.nexy"]
    ROUTE_FILE_DEFAULT = ["index.py", "index.nexy", "index.mdx"]
    PROJECT_ROOT = "."
    ROUTER_PATH = "src/routes"
    useRouter = None

    def __init__(self):
        self._get_config()
        
    def _get_config(self):
        try:
            from nexyconfig import NexyConfig 
            nexy_config = NexyConfig()
            self.ALIASES = getattr(nexy_config, "useAliases", None)
            self.useRouter = getattr(nexy_config, "useRouter", None)
        except Exception:
            return None
