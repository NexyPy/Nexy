from fastapi import FastAPI,Response, Depends
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi.responses import FileResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.types import IncEx
from .router import Router
import sys
from pathlib import Path
from typing import Any, List, Dict, Sequence
from functools import wraps
from scalar_fastapi import get_scalar_api_reference


svg_data_uri ="""data:image/svg+xml;base64,<svg width='100' height='100' viewBox='0 0 100 100' fill='none' xmlns='http://www.w3.org/2000/svg'>
        <rect width='100' height='100' fill='#CBECE3'/>
        <path d='M27 78V22H30.1379L69.2414 60.0575V22H72.2184V78H27Z' fill='#1CB68D'/>
        </svg>
        """
def Nexy(title: str = None , favicon:str = svg_data_uri,**args):
    if title is None:
        title = Path.cwd().name 

    app:FastAPI = FastAPI(title=title,docs_url="/122xxxxxx2345",redoc_url="/xx123n134" , **args)
    
    @app.get("/docs",include_in_schema=False)
    async def scalar_html():

        
        return get_scalar_api_reference(
            openapi_url=app.openapi_url,
            title=app.title,
            scalar_favicon_url= favicon
        )
    app.mount("/public",StaticFiles(directory="public"), name="Public")

    # Configurer le cache
    cache_dir = Path('./__pycache__/nexy')
    cache_dir.mkdir(exist_ok=True)
    sys.pycache_prefix = str(cache_dir)

    app.include_router(Router())
    return app


# Définir le décorateur Params avec tous les paramètres fournis
def Params(
    *,
    response_model: Any = Default(None),
    status_code: int | None = None,
    tags: List[str ] | None = None,
    dependencies: Sequence[Depends] | None = None,
    summary: str | None = None,
    description: str | None = None,
    response_description: str = "Successful Response",
    responses: Dict[int | str, Dict[str, Any]] | None = None,
    deprecated: bool | None = None,
    operation_id: str | None = None,
    response_model_include: IncEx | None = None,
    response_model_exclude: IncEx | None = None,
    response_model_by_alias: bool = True,
    response_model_exclude_unset: bool = False,
    response_model_exclude_defaults: bool = False,
    response_model_exclude_none: bool = False,
    include_in_schema: bool = True,
    response_class: type[Response] | DefaultPlaceholder = Default(JSONResponse),
    name: str | None = None,
    openapi_extra: Dict[str, Any] | None = None,
):
    """
    Un décorateur pour ajouter des paramètres personnalisés à une route.
    """

    def decorator(func):
        # Ajouter tous les paramètres à un dictionnaire
        func.params = {
            "response_model": response_model,
            "status_code": status_code,
            "tags": tags,
            "dependencies": dependencies,
            "summary": summary,
            "description": description,
            "response_description": response_description,
            "responses": responses,
            "deprecated": deprecated,
            "operation_id": operation_id,
            "response_model_include": response_model_include,
            "response_model_exclude": response_model_exclude,
            "response_model_by_alias": response_model_by_alias,
            "response_model_exclude_unset": response_model_exclude_unset,
            "response_model_exclude_defaults": response_model_exclude_defaults,
            "response_model_exclude_none": response_model_exclude_none,
            "include_in_schema": include_in_schema,
            "response_class": response_class,
            "name": name,
            "openapi_extra": openapi_extra,
        }

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Appeler la fonction originale et obtenir son résultat
            result = func(*args, **kwargs)
            return result

        return wrapper

    return decorator

