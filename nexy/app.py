import sys
from pathlib import Path
from typing import Optional, Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from scalar_fastapi import get_scalar_api_reference
from .router import Router


# SVG icon data
SVG_DATA_URI = (
    "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCcgdmlld0JveD0nMCAwIDEwMCAxMDAnIGZpbGw9J25vbmUnIHhtbG5zPSdodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2Zyc+CiAgICAgICAgPHJlY3Qgd2lkdGg9JzEwMCcgaGVpZ2h0PScxMDAnIGZpbGw9JyNCRUNFMycvPgogICAgICAgIDxwYXRoIGQ9J00yNyA3OFYyMkgzMC4xMzc5TDY5LjI0MTQgNjAuMDU3NVYyMkg3Mi4yMTg0Vjc4SDI3WicgZmlsbD0nIzFDQjY4RCcvPgogICAgICAgIDwvc3ZnPgogICAgICAgIA=="
)

def Nexy(title: Optional[str] = None, favicon: str = SVG_DATA_URI, **kwargs: Any) -> FastAPI:
    """
    Creates a FastAPI instance with Nexy configurations.

    Args:
        title: Application title (defaults to current directory name)
        favicon: Icon URL or data URI (defaults to built-in SVG)
        **kwargs: Additional arguments passed to FastAPI constructor
    
    Returns:
        Configured FastAPI instance
    """

    # Configure cache directory
    cache_dir = Path('__pycache__')
    cache_dir.mkdir(parents=True, exist_ok=True)
    sys.pycache_prefix = str(cache_dir)

    # Use current directory name as default title
    title = title or Path.cwd().name

    # Create FastAPI instance
    app = FastAPI(title=title, docs_url=None, redoc_url=None, **kwargs)

    @app.get("/docs", include_in_schema=False)
    async def scalar_docs():
        """Custom API documentation using Scalar."""
        return get_scalar_api_reference(
            servers=["nexy"],
            openapi_url=app.openapi_url,
            title=app.title,
            scalar_favicon_url=favicon,
        )

    # Mount static files if directory exists
    static_dir = Path("public")
    if static_dir.exists():
        app.mount("/public", StaticFiles(directory=static_dir), name="public")

    # Include routers from Router module
    for route in Router():
        app.include_router(route)

    return app