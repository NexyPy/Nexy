from fastapi import FastAPI
from .router import Router
import sys
from pathlib import Path


def Nexy(title: str = "Nexy",**args):
    # Configurer le cache
    app:FastAPI = FastAPI(title,**args)
    cache_dir = Path('./__nexy__')
    cache_dir.mkdir(exist_ok=True)
    sys.pycache_prefix = str(cache_dir)
    Router(appModule=app)
    return app

