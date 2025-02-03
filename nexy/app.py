import os
import sys
from pathlib import Path
from fastapi import APIRouter, FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from .router import Router

# SVG icon data
SVG_DATA_URI = """data:image/svg+xml;base64,<svg width='100' height='100' viewBox='0 0 100 100' fill='none' xmlns='http://www.w3.org/2000/svg'>
        <rect width='100' height='100' fill='#CBECE3'/>
        <path d='M27 78V22H30.1379L69.2414 60.0575V22H72.2184V78H27Z' fill='#1CB68D'/>
        </svg>
        """


def Nexy(title: str = None, favicon: str = SVG_DATA_URI, **args) -> FastAPI:
    """
    Creates a FastAPI instance with base configurations.

    :param title: Application title (defaults to current directory name).
    :param favicon: Icon URL or data (defaults to SVG data defined above).
    :param args: Additional arguments to pass to FastAPI.
    :return: Configured FastAPI instance.
    """
    
    # If no title is passed, use current directory name
    if title is None:
        title = Path.cwd().name 

    # Create FastAPI instance
    app: FastAPI = FastAPI(
        title=title,
        docs_url="/docsx",  # Disable standard docs URL
        redoc_url=None,  # Disable standard redoc URL
        **args
    )
    

    
    @app.get("/docs", include_in_schema=False)
    async def scalar_html():  
        """
        Provides a custom OpenAPI documentation view with defined icon.
        """
        return get_scalar_api_reference(
            servers=["nexy"],
            openapi_url=app.openapi_url,
            title=app.title,
            scalar_favicon_url=favicon,
        )

    # Mount static folder if it exists
    static_dir = "public"
    if os.path.exists(static_dir):
        app.mount("/public", StaticFiles(directory=static_dir), name="public")

    # Include router
    apps = Router()
    for instance in apps:
        app.include_router(instance)

    # Configure cache directory
    cache_dir = Path('.nexy')
    cache_dir.mkdir(parents=True, exist_ok=True)
    sys.pycache_prefix = str(cache_dir)

    return app
