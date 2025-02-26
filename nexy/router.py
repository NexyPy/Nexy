"""
Author: Espoir Loém

This module handles dynamic route loading for the Nexy application.
"""

import asyncio
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Callable, List, Dict, Any, Optional
import logging
import os
import sys
import inspect
from nexy.decorators import actionRegistry
from .utils import deleteFistDotte, dynamicRoute, importModule, convertPathToModulePath

# Analyze the file structure and extract route information
def find_routes(base_path: str) -> List[Dict[str, Any]]:
    routes = []
    
    # Verify if the 'app' folder exists
    if os.path.exists(base_path) and os.path.isdir(base_path):
        # Add app directory to Python path
        app_dir = os.path.abspath(base_path)
        if app_dir not in sys.path:
            sys.path.append(app_dir)
            
        # Explore the 'app' folder and its subfolders
        for root, dirs, files in os.walk(base_path):
            # Remove unwanted folders
            dirs[:] = [d for d in dirs if not d.startswith(("_", "node_module", "env", "venv", "nexy", ".", "public", "configs"))]

            route = {
                "pathname": f"{'/' if os.path.basename(root) == base_path else '/' + deleteFistDotte(os.path.relpath(root, base_path).replace('\\','/'))}",
                "dirName": root
            }
            controller = os.path.join(root, 'controller.py')
            middleware = os.path.join(root, 'middleware.py')
            service = os.path.join(root, 'service.py')
            actions = os.path.join(root, 'actions.py')

            # Check for files and add to dictionary
            if os.path.exists(controller):
                route["controller"] = convertPathToModulePath(f"{root}/controller")    
            if os.path.exists(middleware):
                route["middleware"] = convertPathToModulePath(f"{root}/middleware") 
            if os.path.exists(service):
                route["service"] = convertPathToModulePath(f"{root}/service") 
            if os.path.exists(actions):
                route["actions"] = convertPathToModulePath(f"{root}/actions")
            routes.append(route)

    return routes


class DynamicRouter:
    """
    Class managing dynamic route loading from the 'app' directory.
    """
    HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE","View"]
    
    def __init__(self, base_path: str = "app"):
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        self.apps: List[APIRouter] = []
    
    def load_controller(self, route: Dict[str, Any]) -> Optional[Any]:
        """
        Loads the controller from the specified path.
        """
        try:
            return importModule(path=route["controller"])
        except ModuleNotFoundError as e:
            self.logger.error(f"Controller not found: {route['controller']} - {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading controller {route['controller']}: {str(e)}")
            return None

    def load_middleware(self, route: Dict[str, Any]):
        pass

   
    def registre_actions_http_route(self, app: APIRouter, pathname: str, function: Any, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Registers an HTTP route for actions.
        """
        if params is None:
            params = {"response_class": JSONResponse}
        else:
            params = {k: v for k, v in params.items() if k not in ["tags", "include_in_schema"]}

        app.add_api_route(
            path=pathname,
            endpoint=function,
            methods=["POST"],
            **params,
            tags=["actions"]
        )

    def register_http_route(self, app: APIRouter, pathname: str, function: Any, 
                          method: str, params: Dict[str, Any], dirName: str) -> None:
        """
        Registers an HTTP route with appropriate view and error handling.
        """
        if method == "View":
            app.add_api_route(
                path=pathname,
                endpoint=function,
                methods=["GET"],
                
                **{k: v for k, v in params.items() if k != ["tags", "response_class"]},
                tags=[pathname]
            )

        app.add_api_route(
            path=pathname,
            endpoint=function,
            methods=[method],
            **{k: v for k, v in params.items() if k != "tags"},
            tags=[pathname]
        )

    def register_websocket_route(self, app: APIRouter, pathname: str, 
                               function: Any) -> None:
        """
        Registers a WebSocket route with error handling.
        """
        try:
            app.add_api_websocket_route(f"{pathname}/ws", function)
        except Exception as e:
            self.logger.error(f"Failed to register WebSocket {pathname}: {str(e)}")
            self._register_error_websocket(app, pathname, str(e))

    def _register_error_route(self, app: APIRouter, pathname: str, 
                            method: str, error: str) -> None:
        """
        Registers an error route in case of failure.
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
        Registers a WebSocket error route in case of failure.
        """
        async def error_handler(websocket):
            await websocket.close(code=1011, reason=f"Error: {error}")
            
        app.add_api_websocket_route(f"{pathname}/ws", error_handler)

    def create_routers(self) -> List[APIRouter]:
        """
        Creates and configures all routers from found routes.
        """
        routes = find_routes(base_path=self.base_path)
        actions_routes = actionRegistry.value
        
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

        for route in actions_routes:
            app = APIRouter()
            self.apps.append(app)    
            self.registre_actions_http_route(app, pathname=route["path"], function=route["func"])

        return self.apps

def Router():
    """
    Main function to create the dynamic router.
    """
    router = DynamicRouter()
    return router.create_routers()

def ensure_init_files(base_path: str) -> None:
    """
    Ensures that __init__.py files exist in all directories within the base path.
    """
    for root, dirs, files in os.walk(base_path):
        if '__init__.py' not in files:
            with open(os.path.join(root, '__init__.py'), 'w') as f:
                pass

# Call this function with the base path of your app
ensure_init_files('app')