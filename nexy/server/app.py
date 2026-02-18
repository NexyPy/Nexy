
from fastapi import APIRouter, FastAPI
from nexy.__version__ import __Version__
from nexy.core.config import Config
from nexy.server.routers.file_based_routing import FileBasedRouter


version = __Version__().get()

config = Config()

_server = FastAPI(title="Nexy", version=version)
router_source = config.nexy_config.useRouter if config.nexy_config else None

if isinstance(router_source, FileBasedRouter):
    router_source.register_on(_server)
elif isinstance(router_source, type) and issubclass(router_source, FileBasedRouter):
    router_source().register_on(_server)
elif isinstance(router_source, APIRouter):
    _server.include_router(router_source)
