
from fastapi import FastAPI
from nexy.__version__ import __Version__
from nexy.nexyconfig import NexyConfig
from nexy.server.routers.file_based_routing import FileBasedRouter

version = __Version__().get()
FILE_BASED_ROUTER = FileBasedRouter().route()
config = NexyConfig()

_server = FastAPI(title="Nexy", version=version)

if config.FILE_BASED_ROUTING:
    _server.include_router(FILE_BASED_ROUTER)
else:
    _server.include_router(config.ROOT_MODULE) if config.ROOT_MODULE else None

# if __name__ == "__main__":
#     from uvicorn import run
#     run(_server, host="0.0.0.0", port=8000, reload=True)
