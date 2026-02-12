import uvicorn
from nexy.__version__ import __Version__


def start():
    version = __Version__().get()
    print(f"> nexy@{version} start")
    uvicorn.run("nexy.server.app:_server", host="0.0.0.0", port=8000)