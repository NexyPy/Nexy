
from fastapi import APIRouter, FastAPI
from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.server.routers.file_based_routing import FileBasedRouter

try:
    from nexyconfig import NexyConfig
except Exception:
    NexyConfig = None

version = __Version__().get()

config = Config()

_server = FastAPI(title="Nexy", version=version)

router_source = None

if NexyConfig is not None:
    router_source = getattr(NexyConfig, "useRouter", None)
    if router_source is not None:
        Config.useRouter = router_source

if router_source is None:
    router_source = FileBasedRouter()
    Config.useRouter = router_source

if isinstance(router_source, FileBasedRouter):
    _server.include_router(router_source.route())
elif isinstance(router_source, type) and issubclass(router_source, FileBasedRouter):
    _server.include_router(router_source().route())
elif isinstance(router_source, APIRouter):
    _server.include_router(router_source)

