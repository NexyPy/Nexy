
import os
from fastapi import APIRouter, FastAPI, Response
from fastapi.staticfiles import StaticFiles
from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.routers.file_based_routing import FileBasedRouter
from nexy.utils.console import console


version = __Version__().get()

config: Config = Config()

if config.nexy_config and not getattr(config.nexy_config, "useDocs", True):
    _docs_url = None
    _redocs_url = None
else:
    if config.nexy_config and getattr(config.nexy_config, "useDocsUrl", None) is not None and getattr(config.nexy_config, "useRedocsUrl", None) is not None:
        _docs_url = config.nexy_config.useDocsUrl
        _redocs_url = config.nexy_config.useRedocsUrl
    elif config.nexy_config and getattr(config.nexy_config, "useRedocsUrl", None) is not None:
        _redocs_url = config.nexy_config.useRedocsUrl
        _docs_url = getattr(config.nexy_config, "useDocsUrl", "/docs")
    elif config.nexy_config and getattr(config.nexy_config, "useDocsUrl", None) is not None:
        _docs_url = config.nexy_config.useDocsUrl
        _redocs_url = getattr(config.nexy_config, "useRedocsUrl", "/redocs")
    else:
        _docs_url = "/docs"
        _redocs_url = "/redocs"

svg = """<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="size-6">
  <path stroke-linecap="round" stroke-linejoin="round" d="M7.864 4.243A7.5 7.5 0 0 1 19.5 10.5c0 2.92-.556 5.709-1.568 8.268M5.742 6.364A7.465 7.465 0 0 0 4.5 10.5a7.464 7.464 0 0 1-1.15 3.993m1.989 3.559A11.209 11.209 0 0 0 8.25 10.5a3.75 3.75 0 1 1 7.5 0c0 .527-.021 1.049-.064 1.565M12 10.5a14.94 14.94 0 0 1-3.6 9.75m6.633-4.596a18.666 18.666 0 0 1-2.485 5.33" />
</svg>"""
_server = FastAPI(title="Nexy", version=version, docs_url=_docs_url, redoc_url=_redocs_url )
@_server.get("/favicon.ico", include_in_schema=False)
async def favicon():
    try:
        with open("src/routes/favicon.ico", "rb") as f:
            return Response(content=f.read(), media_type="image/x-icon")
    except FileNotFoundError:
        console.log("src/routes/favicon.ico not found, using default svg")
        return Response(content=svg.encode("utf-8"), media_type="image/x-icon")

# @_server.get("/docs", include_in_schema=False)
# async def custom_swagger_ui_html():
#     return get_swagger_ui_html(
#         openapi_url=_server.openapi_url,
#         title=_server.title + " - Swagger UI",
#         swagger_favicon_url="/public/favicon.ico"  # Chemin vers votre favicon
#     )





if os.path.isdir("public"):
    _server.mount("/public", StaticFiles(directory="public"), name="public")
if os.path.isdir("__nexy__/client"):
    _server.mount("/__nexy__/client", StaticFiles(directory="__nexy__/client"), name="nexy_client")
if os.path.isdir("__nexy__/client"):
    _server.mount("/client", StaticFiles(directory="__nexy__/client"), name="client")
router_source = config.nexy_config.useRouter if config.nexy_config else None

if isinstance(router_source, APIRouter):
    _server.include_router(router_source)
elif isinstance(router_source, type) and issubclass(router_source, APIRouter):
    _server.include_router(router_source())
elif isinstance(router_source, str):
    value = router_source.strip().lower()
    if value in ("file", "file_based", "filebasedrouter", "files"):
        FileBasedRouter().register_on(_server)
elif callable(router_source):
    resolved = router_source()
    if isinstance(resolved, APIRouter):
        _server.include_router(resolved)
    elif isinstance(resolved, type) and issubclass(resolved, APIRouter):
        _server.include_router(resolved())
    elif isinstance(resolved, FileBasedRouter):
        resolved.register_on(_server)
    elif isinstance(resolved, type) and issubclass(resolved, FileBasedRouter):
        resolved().register_on(_server)
else:
    FileBasedRouter().register_on(_server)
