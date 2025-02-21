"""Nexy: A Python framework designed to combine simplicity, performance, and the joy of development."""

__version__ = "0.0.28.3"

from nexy.decorators import Injectable, Config, Inject, HTTPResponse, Describe
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
