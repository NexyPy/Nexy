"""
Nexy: A Python framework designed to combine simplicity, performance, and the joy of development.

Author: Espoir Loém
"""

__version__ = "0.0.28.3"

from nexy.decorators import (
    Injectable, 
    Config, 
    Inject, 
    HTTPResponse, 
    Describe,
    Component,
    Action
)
from nexy.app import Nexy

from fastapi import (
    BackgroundTasks,
    Depends,
    Body,
    Cookie,
    File,
    Form,
    Header,
    Query,
    Security,
    HTTPException,
    Path,
    Request,
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    UploadFile,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    ORJSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)

__all__ = [
    # Nexy-related exports
    "Nexy",
    "Injectable",
    "Config",
    "Inject",
    "HTTPResponse",
    "Describe",
    "Component",
    "Action",
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

# Example usage:
# from nexy import Nexy, Injectable, Config
# app = Nexy()
# @Injectable
# def my_service():
#     return "Service is running"
# @app.get("/")
# async def read_root():
#     return {"message": "Hello, World!"}
