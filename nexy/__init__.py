"""Nexy a Python framework designed to combine simplicity, performance, and the joy of development."""

__version__ = "0.0.28.3"

from nexy.decorators import Injectable as Injectable
from nexy.decorators import Config as Config
from nexy.decorators import Inject as Inject
from nexy.decorators import CustomResponse as CustomResponse
from nexy.decorators import Describe as Describe
from nexy.app import Nexy as Nexy
from nexy.hooks import *

from fastapi import BackgroundTasks as BackgroundTasks
from fastapi import Depends as Depends
from fastapi import Body as Body
from fastapi import Cookie as Cookie
from fastapi import File as File
from fastapi import Form as Form
from fastapi import Header as Header
from fastapi import Query as Query
from fastapi import Security as Security
from fastapi import HTTPException as HTTPException
from fastapi import Path as Path
from fastapi import Request as Request
from fastapi import WebSocket as WebSocket
from fastapi import WebSocketException as WebSocketException
from fastapi import WebSocketDisconnect as WebSocketDisconnect
from fastapi import UploadFile as UploadFile

from fastapi.responses import FileResponse as FileResponse
from fastapi.responses import HTMLResponse as HTMLResponse
from fastapi.responses import JSONResponse as JSONResponse
from fastapi.responses import ORJSONResponse as ORJSONResponse
from fastapi.responses import PlainTextResponse as PlainTextResponse
from fastapi.responses import RedirectResponse as RedirectResponse
from fastapi.responses import Response as Response


__all__ = [
    # Nexy-related exports
    "Nexy",
    "Injectable",
    "Config", 
    "Inject",
    "CustomResponse",
    "Describe",
    
    # FastAPI responses
    "Response",
    "FileResponse",
    "HTMLResponse", 
    "JSONResponse",
    "ORJSONResponse",
    "PlainTextResponse",
    "RedirectResponse",
    
    # FastAPI utilities
    "BackgroundTasks",
    "Depends",
    "Body",
    "Cookie", 
    "File",
    "Form",
    "Header",
    "Query",
    "Security",
    "HTTPException",
    "Path",
    "Request",
    "WebSocket",
    "WebSocketException", 
    "WebSocketDisconnect",
    "UploadFile",
]
