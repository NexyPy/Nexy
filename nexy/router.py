"""
Author: Espoir Loém

This module handles dynamic route loading for the Nexy application.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
import logging
import os
from nexy.decorators import actionRegistry
from .utils import dynamicRoute, find_routes, importModule
from functools import lru_cache


class DynamicRouter:
    """
    Class managing dynamic route loading from the 'app' directory.
    Handles HTTP and WebSocket routes dynamically.
    """
    # Supported HTTP methods according to RFC 7231
    HTTP_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH", "TRACE","View"]
    
    def __init__(self, base_path: str = "app"):
        """
        Initialize router with base path and logging configuration
        """
        self.base_path = base_path
        self.logger = logging.getLogger(__name__)
        self.apps: List[APIRouter] = []
    
    def load_controller(self, route: Dict[str, Any]) -> Optional[Any]:
        """
        Loads the controller from the specified path.
        Returns None if loading fails.
        """
        try:
            controller_path = route["controller"]
            return importModule(path=controller_path)
        except ModuleNotFoundError as e:
            self.logger.error(f"Controller not found: {route['controller']} - {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"Error loading controller {route['controller']}: {str(e)}")
            return None

    def load_middleware(self, route: Dict[str, Any]):
        # TODO: Implement middleware loading logic
        pass

    def registre_actions_http_route(self, app: APIRouter, pathname: str, function: Any, params: Optional[Dict[str, Any]] = None) -> None:
        """
        Registers an HTTP route for actions with default JSON response.
        Filters out unnecessary parameters from the params dictionary.
        """
        params = params or {"response_class": JSONResponse}
        filtered_params = {k: v for k, v in params.items() if k not in ["tags", "include_in_schema"]}

        app.add_api_route(
            path=pathname,
            endpoint=function,
            methods=["POST"],
            **filtered_params,
            tags=["actions"]
        )

    def register_http_route(self, app: APIRouter, pathname: str, function: Any, 
                          method: str, params: Dict[str, Any], dirName: str) -> None:
        """
        Registers an HTTP route with filtered parameters and pathname-based tags.
        Ensures proper route configuration for each HTTP method.
        """
        filtered_params = {k: v for k, v in params.items() if k != "tags"}
        
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
            **filtered_params,
            tags=[pathname]
        )

    def register_websocket_route(self, app: APIRouter, pathname: str, 
                               function: Any) -> None:
        """
        Registers a WebSocket route with error handling.
        Automatically adds /ws suffix to WebSocket endpoints.
        """
        try:
            app.add_api_websocket_route(f"{pathname}/ws", function)
        except Exception as e:
            self.logger.error(f"Failed to register WebSocket {pathname}: {str(e)}")
            self._register_error_websocket(app, pathname, str(e))

    def _register_error_route(self, app: APIRouter, pathname: str, 
                            method: str, error: str) -> None:
        """
        Creates an error handler route for failed HTTP route registrations.
        Returns 500 status code with detailed error information.
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
        Creates an error handler for failed WebSocket route registrations.
        Closes connection with error code 1011 (Internal Error).
        """
        async def error_handler(websocket):
            await websocket.close(code=1011, reason=f"Error: {error}")
            
        app.add_api_websocket_route(f"{pathname}/ws", error_handler)

    def create_routers(self) -> List[APIRouter]:
        """
        Creates and configures all routers from discovered routes.
        Handles both standard routes and action routes.
        Returns list of configured APIRouter instances.
        """
        routes = find_routes(base_path=self.base_path)
        actions_routes = actionRegistry.value
        
        # Process standard routes
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

            # Register routes for each function in controller
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
        
        # Process action routes
        for route in actions_routes:
            app = APIRouter()
            self.apps.append(app)    
            self.registre_actions_http_route(app, pathname=route["path"], function=route["func"])

        return self.apps

def Router():
    """
    Factory function to create and configure the dynamic router.
    Returns list of configured routers.
    """
    router = DynamicRouter()
    return router.create_routers()

def ensure_init_files(base_path: str) -> None:
    """
    Creates __init__.py files in all directories within base_path if missing.
    Essential for Python package structure.
    """
    for root, dirs, files in os.walk(base_path):
        if '__init__.py' not in files:
            with open(os.path.join(root, '__init__.py'), 'w') as f:
                pass

# Initialize application structure
ensure_init_files('app')