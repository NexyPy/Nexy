import importlib
import traceback
from typing import Any

from fastapi import APIRouter, Depends, FastAPI
from fastapi.responses import HTMLResponse

from nexy.core.config import Config
from nexy.core.string import Pathname, StringTransform
from nexy.routers.fbrouter.discovery import RouteDiscovery

# Specialized classes
from .dependencies import RouteDependencies
from .middleware import RouteMiddleware
from .validator import RouteValidator

HTTP_METHODS_MAP = {
    "GET": "get",
    "POST": "post",
    "PUT": "put",
    "DELETE": "delete",
    "PATCH": "patch",
    "OPTIONS": "options",
    "HEAD": "head",
}


class FBRouter:
    def __init__(self) -> None:
        self.discovery = RouteDiscovery()
        self.router = APIRouter()
        self.str_tools = StringTransform()
        self.modules_meta: list[dict[str, Any]] = []
        self.error_handlers: list[dict[str, Any]] = []
        self.notfound_handlers: list[dict[str, Any]] = []

        self._load_and_register()

    def register_on(self, app: FastAPI) -> None:
        app.include_router(self.router)

    def _load_and_register(self):
        self._scan_modules()
        self._register_all_routes()

    def _scan_modules(self):
        for app_path in self.discovery.scan():
            path_str = app_path.as_posix()

            # 1. Resolve Import Path
            if path_str.endswith((".nexy", ".mdx")):
                m_type = "component"
                mapped = self.str_tools.normalize_route_path_for_namespace(path_str)
                import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
            else:
                m_type = "api"
                import_path = path_str.replace("/", ".").removesuffix(".py")
            try:
                module = importlib.import_module(import_path)
            except ImportError:
                module = None
                traceback.print_exc()

            # 2. Process Pathname
            clean = (
                path_str.replace(f"{Config.NAMESPACE}src/routes", "")
                .replace("src/routes", "")
                .split(".")[0]
            )
            pathname = Pathname(clean).process()

            # 3. Categorize (Error, NotFound, or Route)
            name = app_path.name.lower()
            if name in ("error.nexy", "notfound.nexy"):
                scope = Pathname(
                    app_path.parent.as_posix().replace("src/routes", "") or "/"
                ).process()
                entry = {
                    "scope": scope,
                    "module": module,
                    "comp": self.str_tools.get_component_name(name.split(".")[0]),
                }
                if "error" in name:
                    self.error_handlers.append(entry)
                else:
                    self.notfound_handlers.append(entry)
                continue

            self.modules_meta.append(
                {
                    "module": module,
                    "type": m_type,
                    "pathname": pathname,
                    "comp_name": self.str_tools.get_component_name(clean),
                    "source": path_str,
                }
            )

    def _register_all_routes(self):
        for meta in self.modules_meta:
            module, path, source = meta["module"], meta["pathname"], meta["source"]

            # Get folder-level dependencies
            folder_deps = [Depends(d) for d in RouteDependencies.collect(source)]

            if meta["type"] == "api":
                for method, _ in HTTP_METHODS_MAP.items():
                    if handler := getattr(module, method, None):
                        RouteValidator.validate_sig(handler, path, method)

                        # Merge guards, middlewares and folder deps
                        deps = RouteMiddleware.resolve(handler) + folder_deps

                        # Metadata extraction
                        resp_meta = getattr(handler, "__nexy_response_meta__", None)
                        self.router.add_api_route(
                            path=path,
                            endpoint=handler,
                            methods=[method],
                            dependencies=deps or None,
                            name=method,
                            tags=[path],
                            status_code=resp_meta.status_code if resp_meta else None,
                            # ... (other response_meta fields)
                        )

                if ws_handler := getattr(module, "SOCKET", None):
                    self.router.websocket(path)(ws_handler)

            else:  # Component (UI)
                if component := getattr(module, meta["comp_name"], None):
                    deps = RouteMiddleware.resolve(component) + folder_deps
                    self.router.get(
                        path,
                        response_class=HTMLResponse,
                        dependencies=deps or None,
                        name=component.__name__,
                        description=component.__doc__ or "",
                        tags=[path],
                    )(component)
