from fastapi import FastAPI

from .routers.app import _server

app: FastAPI = _server
