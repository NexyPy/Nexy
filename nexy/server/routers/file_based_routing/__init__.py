import importlib
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from nexy.core.string import StringTransform
from nexy.core.config import Config
from nexy.server.routers.file_based_routing.route_discovery import RouteDiscovery

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
                # Enregistrement dynamique des méthodes HTTP
                for method_name, router_method in HTTP_METHODS_MAP.items():
                    if handler := getattr(module, method_name, None):
                        # Récupère la fonction de l'APIRouter (ex: self.router.get)
                        register_func = getattr(self.router, router_method)
                        register_func(path)(handler)
                
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

