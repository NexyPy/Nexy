
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

try:
    from src import middlewares as _nexy_middlewares
except Exception:
    _nexy_middlewares = None

if _nexy_middlewares is not None:
    register = getattr(_nexy_middlewares, "register_middlewares", None)
    if callable(register):
        register(_server)
    else:
        candidates = getattr(_nexy_middlewares, "middlewares", None)
        if isinstance(candidates, (list, tuple)):
            for item in candidates:
                try:
                    cls = getattr(item, "cls", None)
                    options = getattr(item, "options", {}) if hasattr(item, "options") else {}
                    if cls is not None:
                        _server.add_middleware(cls, **options)
                except Exception:
                    continue

router_source = None

if NexyConfig is not None:
    router_source = getattr(NexyConfig, "useRouter", None)
    if router_source is not None:
        Config.useRouter = router_source

if router_source is None:
    router_source = FileBasedRouter()
    Config.useRouter = router_source

if isinstance(router_source, FileBasedRouter):
    router_source.register_on(_server)
elif isinstance(router_source, type) and issubclass(router_source, FileBasedRouter):
    router_source().register_on(_server)
elif isinstance(router_source, APIRouter):
    _server.include_router(router_source)
