"""
Author: Espoir Loém

This module initializes a FastAPI application with Nexy configurations,
including custom API documentation and static file serving.

Classes:
    Nexy: Main application class that handles FastAPI setup and configuration

Attributes:
    SVG_DATA_URI (str): Base64 encoded SVG data for default favicon
"""

import sys
from pathlib import Path
from typing import Optional, Any, Dict, List
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from .router import Router

class Nexy:
    """
    A class to create and configure FastAPI applications with custom settings.
    
    This class provides functionality to:
    - Set up API documentation using Scalar
    - Configure static file serving
    - Handle routing
    - Manage application cache
    
    Attributes:
        title (str): Application title, defaults to current directory name
        favicon (str): URL or data URI for favicon
        config (Dict): Additional configuration options
    """
    
    SVG_DATA_URI = (
        "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDEwMCAxMDAnIGZpbGw9J25vbmUnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zyc+CiAgICAgICAgPHJlY3Qgd2lkd2g9JzEwMCcgaGVpZ2h0PScxMDAnIGZpbGw9JyNCRUNFMycvPgogICAgICAgIDxwYXRoIGQ9J00yNyA3OFYyMkgzMC4xMzc5TDY5LjI0MTQgNjAuMDU3NVYyMkg3Mi4yMTg0Vjc4SDI3WicgZmlsbD0nIzFDQjY4RCcvPgogICAgICAgIDwvc3ZnPgogICAgICAgIA=="
    )

    def __init__(
        self,
        title: Optional[str] = None,
        favicon: str = SVG_DATA_URI,
        config: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> None:
        """
        Initialize a new Nexy application.

        Args:
            title (Optional[str]): Application title. Defaults to current directory name.
            favicon (str): Favicon URL or data URI. Defaults to SVG_DATA_URI.
            config (Optional[Dict[str, Any]]): Additional configuration options.
            **kwargs: Additional arguments passed to FastAPI constructor.
        """
        self.title = title or Path.cwd().name
        self.favicon = favicon
        self.config = config or {}
        self.kwargs = kwargs
        self.app = self._create_app()
        self._setup_app()

    def _create_app(self) -> FastAPI:
        """
        Creates and configures the FastAPI instance.
        
        Returns:
            FastAPI: Configured FastAPI application instance.
        """
        self._setup_cache()
        return FastAPI(
            title=self.title,
            docs_url=None,
            redoc_url=None,
            **self.kwargs
        )

    def _setup_cache(self) -> None:
        """
        Configures the cache directory for the application.
        Creates __pycache__ directory if it doesn't exist.
        """
        cache_dir = Path('__pycache__')
        cache_dir.mkdir(parents=True, exist_ok=True)
        sys.pycache_prefix = str(cache_dir)

    def _setup_app(self) -> None:
        """
        Sets up all application components including documentation,
        static files, and routes.
        """

        self._setup_docs(pathName= self.config.get("docs_path") if self.config.get("docs_path") else "docs")
        self._setup_static_files()
        self._setup_routes()

    def _setup_docs(self,pathName:str="docs") -> None:
        """
        Configures API documentation using Scalar.
        Creates a /docs endpoint that serves the API reference.
        """
        @self.app.get(f"/{pathName}", include_in_schema=False)
        async def scalar_docs():
            return get_scalar_api_reference(
                servers=["nexy"],
                openapi_url=self.app.openapi_url,
                title=self.app.title,
                scalar_favicon_url=self.favicon,
            )

    def _setup_static_files(self) -> None:
        """
        Mounts static file directories for public assets and actions.
        Creates routes for /public and /nexy_public if directories exist.
        """
        static_dir = Path("public")
        actions_dir = Path("__pycache__/nexy/")
        
        if static_dir.exists():
            self.app.mount("/public", StaticFiles(directory=static_dir), name="public")
        if actions_dir.exists():
            self.app.mount("/nexy_public", StaticFiles(directory=actions_dir), name="actions")

    def _setup_routes(self) -> None:
        """
        Includes application routes from the Router instance.
        Registers all routes with the FastAPI application.
        """
        for route in Router():
            self.app.include_router(route)

    def __call__(self) -> FastAPI:
        """
        Makes the class callable to return the FastAPI instance.
        
        Returns:
            FastAPI: The configured FastAPI application instance.
        """
        return self.app