from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from typing import List, Dict, Any, Optional
import logging
import os
import sys

from nexy.hooks import useView
from .utils import deleteFistDotte, dynamicRoute, importModule, convertPathToModulePath

# Analyze the file structure and extract route information
def FIND_ROUTES(base_path):
    routes: list = []
    
    # Verify if the 'app' folder exists
    if os.path.exists(base_path) and os.path.isdir(base_path):
        # Add app directory to Python path
        app_dir = os.path.abspath(base_path)
        if app_dir not in sys.path:
            sys.path.append(app_dir)
            
        # Explore the 'app' folder and its subfolders
        for root, dirs, files in os.walk(base_path):
            # Remove _folders
            dirs[:] = [d for d in dirs if not d.startswith("_")]

            route = {
                "pathname": f"{'/' if os.path.basename(root) == base_path else '/' + deleteFistDotte(os.path.relpath(root, base_path).replace('\\','/'))}",
                "dirName": root
            }
            controller = os.path.join(root, 'controller.py')
            middleware = os.path.join(root, 'middleware.py')
            service = os.path.join(root, 'service.py')

            # Check for files and add to dictionary
            if os.path.exists(controller):
                route["controller"] = convertPathToModulePath(f"{root}/controller")    
            if os.path.exists(middleware):
                route["middleware"] = convertPathToModulePath(f"{root}/middleware") 
            if os.path.exists(service):
                route["service"] = convertPathToModulePath(f"{root}/service") 
            routes.append(route)

    return routes


class DynamicRouter:
    """
    Classe gérant le chargement dynamique des routes depuis le répertoire 'app'.
    """
    HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE"]
    
    def __init__(self, base_path: str = "app"):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        self.apps: List[APIRouter] = []

    def load_controller(self, route: Dict[str, Any]) -> Optional[Any]:
        """
        Charge le contrôleur à partir du chemin spécifié.
        """
        try:
            return importModule(path=route["controller"])
        except ModuleNotFoundError as e:
            self.logger.error(f"Controller not found: {route['controller']} - {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading controller {route['controller']}: {str(e)}")
            return None

    def register_http_route(self, app: APIRouter, pathname: str, function: Any, 
                          method: str, params: Dict[str, Any], dirName:str) -> None:
        """
        Enregistre une route HTTP avec gestion appropriée des vues et des erreurs.
        """
        try:
            if params.get("response_class") == HTMLResponse:
                def view(data = Depends(function)):
                    return useView(
                        data=data,
                        path=dirName.strip("/").replace("\\", "/")
                    )
                endpoint = view
            else:
                endpoint = function

            app.add_api_route(
                path=pathname,
                endpoint=endpoint,
                methods=[method],
                **{k: v for k, v in params.items() if k != "tags"},
                tags=[pathname]
            )
        except Exception as e:
            self.logger.error(f"Failed to register route {pathname} [{method}]: {str(e)}")
            self._register_error_route(app, pathname, method, str(e))

    def register_websocket_route(self, app: APIRouter, pathname: str, 
                               function: Any) -> None:
        """
        Enregistre une route WebSocket avec gestion des erreurs.
        """
        try:
            app.add_api_websocket_route(f"{pathname}/ws", function)
        except Exception as e:
            self.logger.error(f"Failed to register WebSocket {pathname}: {str(e)}")
            self._register_error_websocket(app, pathname, str(e))

    def _register_error_route(self, app: APIRouter, pathname: str, 
                            method: str, error: str) -> None:
        """
        Enregistre une route d'erreur en cas d'échec.
        """
        async def error_handler():
            raise HTTPException(
                status_code=500,
                detail=f"Error in method {method} for route {pathname}: {error}"
            )
        
        app.add_api_route(
            path=pathname,
            endpoint=error_handler,
            methods=[method],
            status_code=500
        )

    def _register_error_websocket(self, app: APIRouter, pathname: str, 
                                error: str) -> None:
        """
        Enregistre une route WebSocket d'erreur en cas d'échec.
        """
        async def error_handler(websocket):
            await websocket.close(code=1011, reason=f"Error: {error}")
            
        app.add_api_websocket_route(f"{pathname}/ws", error_handler)

    def create_routers(self) -> List[APIRouter]:
        """
        Crée et configure tous les routeurs à partir des routes trouvées.
        """
        routes = FIND_ROUTES(base_path=self.base_path)
        
        for route in routes:
            app = APIRouter()
            self.apps.append(app)
            
            if "controller" not in route:
                continue

            pathname = dynamicRoute(route_in=route["pathname"])
            dirName = route["dirName"]
            controller = self.load_controller(route)
            
            if not controller:
                continue

            for function_name in dir(controller):
                function = getattr(controller, function_name)
                
                if not (callable(function) and hasattr(function, "__annotations__")):
                    continue
                    
                params = getattr(function, "params", {})
                
                if function_name in self.HTTP_METHODS:
                    self.register_http_route(app, pathname, function, 
                                          function_name, params, dirName)
                elif function_name == "SOCKET":
                    self.register_websocket_route(app, pathname, function)

        return self.apps

def Router():
    """
    Fonction principale pour créer le routeur dynamique.
    """
    router = DynamicRouter()
    return router.create_routers()