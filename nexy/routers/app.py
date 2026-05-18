import os
from collections.abc import Callable
from pathlib import Path

from fastapi import APIRouter, FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from starlette.exceptions import HTTPException

from nexy.__version__ import __Version__

# from nexy.utils.dev.pycache import pycache
from nexy.core.config import Config
from nexy.decorators import Container
from nexy.errors import InternalServerError, NotFound
from nexy.routers.actions.engine import ACTION_ENGINE
from nexy.routers.context import current_request
from nexy.routers.fbrouter import FBRouter
from nexy.runtime.hmr import HMR_MANAGER
from nexy.runtime.importer import install_vfs_importer
from nexy.utils.common.console import console


class AppServer:
    def __init__(self):
        install_vfs_importer()
        self.config = Config()
        self.version = __Version__().get()
        self.server: FastAPI | None = None

        # Internal configuration state
        self._docs_url, self._redocs_url = self._resolve_docs_settings()

    async def scalar_html(self):
        return get_scalar_api_reference(
            scalar_favicon_url="/favicon.ico",
            openapi_url=self.server.openapi_url,
            title="Nexy - scalar API",
            telemetry=True,
            dark_mode=True,
            hide_models=True,
            scalar_proxy_url="https://proxy.scalar.com",
        )

    def _resolve_docs_settings(self):
        """KISS: Logic extracted to a single specialized method."""
        conf = self.config
        if not conf.useDocs:
            console.print("[yellow]API documentation is disabled[/yellow]")
            return None, None

        d_url = conf.useDocsUrl
        r_url = conf.useRedocsUrl
        return d_url, r_url

    def _setup_static_files(self):
        """Mounts directories if they exist."""
        mounts = {"/public": "public", "/assets": "__nexy__/client/assets"}
        for path, directory in mounts.items():
            if os.path.isdir(directory):
                self.server.mount(path, StaticFiles(directory=directory), name=directory)

    def _setup_favicon(self):
        """Handle favicon route."""
        svg = """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M7.864 4.243A7.5 7.5 0 0 1 19.5 10.5c0 2.92-.556 5.709-1.568 8.268M5.742 6.364A7.465 7.465 0 0 0 4.5 10.5a7.464 7.464 0 0 1-1.15 3.993m1.989 3.559A11.209 11.209 0 0 0 8.25 10.5a3.75 3.75 0 1 1 7.5 0c0 .527-.021 1.049-.064 1.565M12 10.5a14.94 14.94 0 0 1-3.6 9.75m6.633-4.596a18.666 18.666 0 0 1-2.485 5.33" /></svg>"""

        @self.server.get("/favicon.ico", include_in_schema=False)
        async def favicon():
            try:
                with open("src/routes/favicon.ico", "rb") as f:
                    return Response(content=f.read(), media_type="image/x-icon")
            except FileNotFoundError:
                return Response(content=svg.encode("utf-8"), media_type="image/x-icon")

    def _resolve_router(self):
        """SOLID: Decoupled router resolution logic."""

        router_source = self.config.useRouter
        # 1. Direct APIRouter or Class

        if self._docs_url:
            self.server.get(self._docs_url, include_in_schema=False)(self.scalar_html)

        ACTION_ENGINE.include_router(self.server)

        if isinstance(router_source, (APIRouter, type)) and (
            isinstance(router_source, APIRouter) or issubclass(router_source, APIRouter)
        ):
            console.print("[dim]Nexy  use useRouter from nexyconfig.py[/dim]")
            self.server.include_router(router_source)
        elif Path("src/routes").exists():
            console.print("[dim]Nexy use FB Router[/dim]")
            FBRouter().register_on(self.server)

    async def PathMiddleware(self, request: Request, call_next: Callable) -> Response:
        token = current_request.set(request)
        try:
            response = await call_next(request)
            return response
        finally:
            current_request.reset(token)
            Container.clear_request_scope()

    def _register_error_handlers(self, request: Request, exc: HTTPException) -> Response:
        """Registers custom error handlers for 404 and 500 errors."""
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            # Handle 404 error
            return NotFound()
        elif exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            # Handle 500 error
            return InternalServerError()
        else:
            # For other HTTP exceptions, return the default response
            return Response(
                content=f"<h1>{exc.status_code} - {exc.detail}</h1>", status_code=exc.status_code
            )

    def _setup_hmr(self):
        """Setup WebSocket for Hot Module Replacement in development."""
        # Only in dev mode
        import asyncio

        from fastapi import WebSocket, WebSocketDisconnect

        # Store the current loop for HMR access from other threads
        HMR_MANAGER.loop = asyncio.get_event_loop()

        @self.server.websocket("/_nexy/hmr")
        async def hmr_endpoint(websocket: WebSocket):
            await HMR_MANAGER.connect(websocket)
            try:
                while True:
                    # Keep connection alive
                    await websocket.receive_text()
            except (WebSocketDisconnect, Exception):
                HMR_MANAGER.disconnect(websocket)

    def _setup_middlewares(self) -> None:
        config = self.config
        middlewares: list = []

        if config.useCORS:
            middlewares.append((CORSMiddleware, config.useCORS))
        if config.useGZip:
            middlewares.append((GZipMiddleware, config.useGZip))
        if config.useTrustedHost:
            middlewares.append((TrustedHostMiddleware, config.useTrustedHost))
        if config.useSession:
            try:
                from starlette.middleware.sessions import SessionMiddleware

                middlewares.append((SessionMiddleware, config.useSession))
            except ImportError:
                console.print("[yellow]  install 'itsdangerous' for SessionMiddleware[/yellow]")
        if config.useAuth:
            try:
                from starlette.middleware.authentication import AuthenticationMiddleware

                middlewares.append((AuthenticationMiddleware, config.useAuth))
            except ImportError:
                console.print("[yellow]  install 'httpx' for AuthenticationMiddleware[/yellow]")
        for entry in config.useMiddlewares:
            if isinstance(entry, tuple) and len(entry) == 2:
                middlewares.append(entry)

        for cls, kwargs in middlewares:
            self.server.add_middleware(cls, **kwargs)

        if config.useHTTPSRedirect:
            self.server.add_middleware(HTTPSRedirectMiddleware)

    def run(self) -> FastAPI:
        """Main entry point to assemble the application."""
        # pycache()

        self.server = FastAPI(title="Nexy", version=self.version, docs_url=None, redoc_url=None)

        self.server.middleware("http")(self.PathMiddleware)
        self._setup_favicon()
        self._setup_static_files()
        self._setup_middlewares()
        self._resolve_router()
        self._setup_hmr()
        self.server.exception_handler(HTTPException)(self._register_error_handlers)
        return self.server


_server = AppServer().run()
