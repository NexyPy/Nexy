import importlib
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from nexy.core.string import StringTransform
from nexy.core.config import Config
from nexy.server.routers.file_based_routing.route_discovery import RouteDiscovery
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
        
        self._load_modules()
        self._register_routes()

    def route(self) -> APIRouter:
        return self.router

    def _load_modules(self) -> None:
        """Scanne les fichiers et prépare les métadonnées des routes."""
        for app_path in self.route_discovery.scan():
            path_str = app_path.as_posix()
            
            # Détermination du type et du chemin d'import
            if path_str.endswith((".nexy", ".mdx")):
                type_module = "component"
                import_path = f"{Config.NAMESPACE}{path_str}".replace("/", ".").rsplit(".", 1)[0]
            else:
                type_module = "api"
                import_path = path_str.replace("/", ".").removesuffix(".py")

            module = importlib.import_module(import_path)
            
            # Nettoyage propre du pathname URL
            # On retire les préfixes de dossiers sources pour obtenir l'URL
            clean_path = path_str.replace(f"{Config.NAMESPACE}src/routes", "").replace("src/routes", "")
            clean_path = clean_path.split(".")[0] # Retire l'extension
            
            pathname = clean_path.removesuffix("/index")
            if not pathname:
                pathname = "/"

            # print(f"Discovered route: {pathname} -> {import_path} ({type_module})")
            
            self.modules_metadata.append({
                "module": module,
                "type": type_module,
                "pathname": pathname,
                "component_name": self.string_transform.get_component_name(clean_path)
            })

    def _register_routes(self) -> None:
        """Enregistre les routes dans l'APIRouter de FastAPI."""
        for meta in self.modules_metadata:
            module = meta["module"]
            path = meta["pathname"]

            if meta["type"] == "api":
                for method_name, router_method in HTTP_METHODS_MAP.items():
                    handler = getattr(module, method_name, None)
                    if handler is None:
                        continue
                    route_meta: RouteMeta | None = getattr(handler, "__nexy_route_meta__", None)
                    response_meta: ResponseMeta | None = getattr(handler, "__nexy_response_meta__", None)
                    guards = getattr(handler, "__nexy_guards__", ())
                    middlewares = getattr(handler, "__nexy_middlewares__", ())
                    dependencies = [
                        Depends(dep)
                        for dep in (*guards, *middlewares)
                    ] or None
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
                    self.router.websocket(path)(handler)
            
            else:
                # Enregistrement des composants UI
                if component := getattr(module, meta["component_name"], None):
                    self.router.get(
                        path,
                        response_class=HTMLResponse,
                        name=meta["component_name"]
                    )(component)

