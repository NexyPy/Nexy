"""
Nexy: A Python framework designed to combine simplicity, performance, and the joy of development.

A modern, efficient framework that prioritizes developer experience while maintaining high performance.

Author: Espoir Loémba
Version: 0.1.3
"""

# Version identifier
__version__  = "0.1.3"

# Import core Nexy decorators and functionality
import  nexy.decorators, nexy.app

Injectable = nexy.decorators.Injectable
Config = nexy.decorators.Config
Inject = nexy.decorators.Inject
HTTPResponse = nexy.decorators.HTTPResponse
Describe = nexy.decorators.Describe
action = nexy.decorators.action
Nexy = nexy.app.Nexy


# Import FastAPI core components for request handling and utilities
import  fastapi ,fastapi.responses,fastapi.websockets 

BackgroundTasks = fastapi.BackgroundTasks    # Async background task handling
Depends = fastapi.Depends                    # Dependency injection system
Body = fastapi.Body                          # Request body parser
Cookie = fastapi.Cookie                      # Cookie parameter parser
File = fastapi.File                          # File handling
Form = fastapi.Form                          # Form data parser
Header = fastapi.Header                      # Header parameter parser
Query = fastapi.Query                        # Query parameter parser
Security = fastapi.Security                  # Security utilities
HTTPException = fastapi.HTTPException        # HTTP error handling
Path = fastapi.Path                          # Path parameter parser
Request = fastapi.Request                    # Raw request object
WebSocket = fastapi.WebSocket                # WebSocket support
WSState = fastapi.websockets.WebSocketState

WebSocketException = fastapi.WebSocketException # WebSocket error handling
WebSocketDisconnect = fastapi.WebSocketDisconnect # WebSocket disconnect handling
UploadFile = fastapi.UploadFile             # File upload handling

# Import FastAPI response types for various content formats

FileResponse = fastapi.responses.FileResponse,       # File serving
HTMLResponse = fastapi.responses.HTMLResponse,       # HTML content
JSONResponse = fastapi.responses.JSONResponse,       # JSON data
ORJSONResponse = fastapi.responses.ORJSONResponse,     # High-performance JSON
PlainTextResponse = fastapi.responses.PlainTextResponse,  # Plain text
RedirectResponse = fastapi.responses.RedirectResponse,   # URL redirections
Response = fastapi.responses.Response, 



