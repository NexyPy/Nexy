import importlib
import inspect
import re
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path
import functools
from fastapi import APIRouter, Depends, HTTPException, Request, FastAPI
from fastapi.responses import HTMLResponse

from nexy.core.string import StringTransform, Pathname
from nexy.core.config import Config
from nexy.routers.file_based_routing.route_discovery import RouteDiscovery
from nexy.decorators import RouteMeta, ResponseMeta

# Configuration des méthodes supportées
HTTP_METHODS_MAP = {
    "GET": "get",
    "POST": "post",
    "PUT": "put",
    "DELETE": "delete",
    "PATCH": "patch",
    "OPTIONS": "options",
    "HEAD": "head",
}

class FileBasedRouter:
    def __init__(self) -> None:
        self.route_discovery = RouteDiscovery()
        self.router = APIRouter()
        self.string_transform = StringTransform()
        self.modules_metadata: list[dict] = []
        self.error_components: list[dict] = []
        self.notfound_components: list[dict] = []
        
        self._load_modules()
        self._register_routes()

    def route(self) -> APIRouter:
        return self.router

    def _collect_route_dependencies(self, path_str: str) -> list[Callable[..., Any]]:
        deps: list[Callable[..., Any]] = []
        try:
            from pathlib import Path

            path = Path(path_str)
            root = Path(Config.ROUTER_PATH).resolve()
            current = path.parent.resolve()

            chain: list[Path] = []
            while str(current).startswith(str(root)):
                chain.append(current)
                if current == root:
                    break
                current = current.parent

            for directory in reversed(chain):
                dep_file = directory / "dependencies.py"
                if dep_file.is_file():
                    rel = directory.as_posix().replace("/", ".")
                    module_path = f"{rel}.dependencies"
                    try:
                        mod = importlib.import_module(module_path)
                    except Exception:
                        continue
                    candidates = getattr(mod, "dependencies", None)
                    if isinstance(candidates, (list, tuple)):
                        for c in candidates:
                            if callable(c):
                                deps.append(c)
        except Exception:
            return deps
        return deps

    def _extract_path_params(self, path: str) -> set[str]:
        return {m.group(1) for m in re.finditer(r"{([^}:]+)(:[^}]+)?}", path)}

    def _validate_handler_signature(
        self,
        handler: Callable[..., Any],
        path: str,
        source_path: str,
        method_name: str,
    ) -> None:
        expected = self._extract_path_params(path)
        if not expected:
            return
        try:
            sig = inspect.signature(handler)
        except ValueError:
            return
        params = set(sig.parameters.keys())
        missing = expected - params
        if missing:
            missing_str = ", ".join(sorted(missing))
            raise RuntimeError(
                f"Incohérence entre le chemin '{path}' et la signature de '{method_name}' "
                f"dans '{source_path}': paramètres manquants {missing_str}"
            )

    def register_on(self, app: FastAPI) -> None:
        app.include_router(self.router)
        app.add_exception_handler(Exception, self._handle_unexpected_error)

    def _load_modules(self) -> None:
        """Scanne les fichiers et prépare les métadonnées des routes."""
        for app_path in self.route_discovery.scan():
            path_str = app_path.as_posix()
            
            # Détermination du type et du chemin d'import
            if path_str.endswith((".nexy", ".mdx")):
                type_module = "component"
                from nexy.core.string import StringTransform as _ST
                mapped = _ST.normalize_route_path_for_namespace(path_str)
                import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]
            else:
                type_module = "api"
                import_path = path_str.replace("/", ".").removesuffix(".py")

            module = importlib.import_module(import_path)
            
            clean_path = path_str.replace(f"{Config.NAMESPACE}src/routes", "").replace("src/routes", "")
            clean_path = clean_path.split(".")[0]
            pathname = Pathname(clean_path).process()

            name_only = app_path.name
            if name_only.lower() == "error.nexy":
                scope = app_path.parent.as_posix().replace("src/routes", "") or "/"
                scope_path = Pathname(scope).process()
                self.error_components.append(
                    {
                        "scope": scope_path,
                        "module": module,
                        "component_name": self.string_transform.get_component_name("Error"),
                    }
                )
                continue

            if name_only.lower() == "notfound.nexy":
                scope = app_path.parent.as_posix().replace("src/routes", "") or "/"
                scope_path = Pathname(scope).process()
                self.notfound_components.append(
                    {
                        "scope": scope_path,
                        "module": module,
                        "component_name": self.string_transform.get_component_name("notfound"),
                    }
                )
                continue

            self.modules_metadata.append(
                {
                    "module": module,
                    "type": type_module,
                    "pathname": pathname,
                    "component_name": self.string_transform.get_component_name(clean_path),
                    "source_path": path_str,
                }
            )

    def _resolve_scoped_component(
        self,
        path: str,
        entries: List[Dict[str, Any]],
    ) -> Optional[Callable[..., Any]]:
        best: Optional[Dict[str, Any]] = None
        for entry in entries:
            scope = entry["scope"]
            if scope == "/":
                match = True
            else:
                match = path.startswith(scope.rstrip("/"))
            if match:
                if best is None or len(scope) > len(best["scope"]):
                    best = entry
        if best is None:
            return None
        component = getattr(best["module"], best["component_name"], None)
        if component is None:
            return None
        return component

    async def _handle_not_found(self, request: Request, path: str) -> HTMLResponse:
        component = self._resolve_scoped_component(request.url.path, self.notfound_components)
        if component is None:
            raise HTTPException(status_code=404, detail="Not Found")
        html = component()
        return HTMLResponse(content=html, status_code=404)

    async def _handle_unexpected_error(self, request: Request, exc: Exception) -> HTMLResponse:
        component = self._resolve_scoped_component(request.url.path, self.error_components)
        if component is None:
            raise exc
        html = component()
        return HTMLResponse(content=html, status_code=500)

    def _register_routes(self) -> None:
        """Enregistre les routes dans l'APIRouter de FastAPI."""
        for meta in self.modules_metadata:
            module = meta["module"]
            path = meta["pathname"]
            source_path = meta["source_path"]

            route_level_deps = self._collect_route_dependencies(source_path)

            if meta["type"] == "api":
                for method_name, router_method in HTTP_METHODS_MAP.items():
                    handler = getattr(module, method_name, None)
                    if handler is None:
                        continue
                    self._validate_handler_signature(handler, path, source_path, method_name)
                    route_meta: RouteMeta | None = getattr(handler, "__nexy_route_meta__", None)
                    response_meta: ResponseMeta | None = getattr(handler, "__nexy_response_meta__", None)
                    guards = getattr(handler, "__nexy_guards__", ())
                    middlewares = getattr(handler, "__nexy_middlewares__", ())
                    deps_callables = [*guards, *middlewares, *route_level_deps]
                    dependencies = [Depends(dep) for dep in deps_callables] or None
                    name = route_meta.name if route_meta and route_meta.name else None
                    tags = route_meta.tags if route_meta and route_meta.tags is not None else None
                    route_kwargs: dict[str, object] = {
                        "path": path,
                        "endpoint": handler,
                        "methods": [method_name],
                        "name": name,
                        "tags": tags,
                        "dependencies": dependencies,
                    }
                    if response_meta is not None:
                        if response_meta.status_code is not None:
                            route_kwargs["status_code"] = response_meta.status_code
                        if response_meta.response_class is not None:
                            route_kwargs["response_class"] = response_meta.response_class
                        if response_meta.response_model is not None:
                            route_kwargs["response_model"] = response_meta.response_model
                        if response_meta.responses is not None:
                            route_kwargs["responses"] = response_meta.responses
                        if response_meta.response_description is not None:
                            route_kwargs["response_description"] = response_meta.response_description
                        if response_meta.response_model_include is not None:
                            route_kwargs["response_model_include"] = response_meta.response_model_include
                        if response_meta.response_model_exclude is not None:
                            route_kwargs["response_model_exclude"] = response_meta.response_model_exclude
                        if response_meta.response_model_by_alias is not None:
                            route_kwargs["response_model_by_alias"] = response_meta.response_model_by_alias
                        if response_meta.response_model_exclude_unset is not None:
                            route_kwargs["response_model_exclude_unset"] = response_meta.response_model_exclude_unset
                        if response_meta.response_model_exclude_defaults is not None:
                            route_kwargs["response_model_exclude_defaults"] = response_meta.response_model_exclude_defaults
                        if response_meta.response_model_exclude_none is not None:
                            route_kwargs["response_model_exclude_none"] = response_meta.response_model_exclude_none
                    self.router.add_api_route(**route_kwargs)
                
                # Cas spécial WebSocket
                if handler := getattr(module, "SOCKET", None):
                    self._validate_handler_signature(handler, path, source_path, "SOCKET")
                    self.router.websocket(path)(handler)
            
            else:
                # Enregistrement des composants UI
                if component := getattr(module, meta["component_name"], None):
                    wrapped = self._wrap_component_with_layout(component, meta["source_path"])
                    self.router.get(
                        path,
                        response_class=HTMLResponse,
                        name=meta["component_name"],
                        dependencies=[Depends(dep) for dep in route_level_deps] or None,
                    )(wrapped)

        self.router.add_api_route(
            "/{path:path}",
            self._handle_not_found,
            methods=["GET"],
            response_class=HTMLResponse,
        )

    def _wrap_component_with_layout(self, component: Callable[..., Any], source_path: str) -> Callable[..., Any]:
        sig = inspect.signature(component)
        @functools.wraps(component)
        def endpoint(*args, **kwargs):
            inner = component(*args, **kwargs)
            html = self._apply_layout(inner, source_path)
            return html
        endpoint.__signature__ = sig
        return endpoint

    def _apply_layout(self, inner_html: str, source_path: str) -> str:
        try:
            tpl_path = Path(source_path)
            parts = list(tpl_path.parent.parts)
            try:
                idx_routes = parts.index("routes")
            except ValueError:
                dirs: list[Path] = []
            else:
                base = parts[: idx_routes + 1]
                dirs = [Path(*base)]
                for extra in parts[idx_routes + 1 :]:
                    base = base + [extra]
                    dirs.append(Path(*base))
            for directory in reversed(dirs):
                from nexy.core.string import StringTransform as _ST
                normalized = _ST.normalize_route_path_for_namespace(f"{directory.as_posix()}/layout.nexy")
                module_path = f"{Config.NAMESPACE}{normalized}".replace("/", ".").rsplit(".", 1)[0]
                try:
                    mod = importlib.import_module(module_path)
                except Exception:
                    continue
                layout = getattr(mod, "Layout", None)
                if callable(layout):
                    return layout(children=inner_html)
        except Exception:
            return inner_html
        return inner_html

