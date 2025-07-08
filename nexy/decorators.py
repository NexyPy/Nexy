"""
Author: Espoir Loém

This module provides various decorators for use in the Nexy framework, including dependency injection,
HTTP response handling, and component rendering.
"""

# Import required modules
import asyncio
from functools import wraps, lru_cache
import hashlib
import inspect
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, Union
from pathlib import Path

# Import FastAPI related dependencies
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi import APIRouter, Depends, Request 
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse
from fastapi.types import IncEx

from nexy.utils import generate_js_action

# Type definitions
T = TypeVar("T")
DependencyType = Union[Callable[..., Any], Type[Any]]

def Injectable() -> Any:
    """
    Decorator that marks a function as injectable for dependency injection.
    Returns a wrapped function that can be used with FastAPI's Depends.
    """
    def decorator(func):
        return wraps(func)(lambda *args, **kwargs: Depends(func(*args, **kwargs)))
    return decorator

def Inject(dependencies: Sequence[Depends] | None = None):
    """
    Decorator for injecting dependencies into a function.
    Args:
        dependencies: Sequence of dependencies to inject
    """
    def decorator(func):
        func.params = {"dependencies": dependencies}
        return wraps(func)(lambda *args, **kwargs: func(*args, **kwargs))
    return decorator

def HTTPResponse(
        model: Any = Default(None),
        response_map: Dict[int | str, Dict[str, Any]] | None = None,       
        model_include: IncEx | None = None,
        model_exclude: IncEx | None = None,
        model_by_alias: bool = True,
        model_exclude_unset: bool = False,
        model_exclude_defaults: bool = False,
        model_exclude_none: bool = False,
        type: type[FastAPIResponse] | DefaultPlaceholder = Default(JSONResponse),
         ):
    """
    Decorator for configuring HTTP response parameters.
    Args:
        model: Response model type
        response_map: Mapping of status codes to response configurations
        model_include: Fields to include in response
        model_exclude: Fields to exclude from response
        model_by_alias: Whether to use alias names
        model_exclude_unset: Whether to exclude unset fields
        model_exclude_defaults: Whether to exclude default values
        model_exclude_none: Whether to exclude None values
        type: Response class type
    """
    def decorator(func):
        func.params = {
            "response_model": model,
            "response_model_include": model_include,
            "response_model_exclude": model_exclude,
            "response_model_by_alias": model_by_alias,
            "response_model_exclude_unset": model_exclude_unset,
            "response_model_exclude_defaults": model_exclude_defaults,
            "response_model_exclude_none": model_exclude_none,
            "response_class": type,
            "responses": response_map
        }
        return wraps(func)(lambda *args, **kwargs: func(*args, **kwargs))
    return decorator

def Describe(
      summary: str | None = None,
      description: str | None = None,
      response: str = "Successful Response",
      ):
    """
    Decorator for adding OpenAPI documentation details.
    Args:
        summary: Brief summary of the endpoint
        description: Detailed description of the endpoint
        response: Description of successful response
    """
    def decorator(func):
        func.params = {
            "summary": summary,
            "description": description,
            "response_description": response,
        }
        return wraps(func)(lambda *args, **kwargs: func(*args, **kwargs))
    return decorator

def Config(
        status_code: int | None = None,
        deprecated: bool | None = None,
        operation_id: str | None = None,
        include_in_schema: bool = True,
        name: str | None = None,
        openapi_extra: Dict[str, Any] | None = None,
        ):
    """
    Decorator for configuring endpoint behavior.
    Args:
        status_code: HTTP status code
        deprecated: Whether the endpoint is deprecated
        operation_id: Unique operation ID
        include_in_schema: Whether to include in OpenAPI schema
        name: Custom name for the endpoint
        openapi_extra: Additional OpenAPI specifications
    """
    def decorator(func):
        func.params = {
            "deprecated": deprecated,
            "operation_id": operation_id,
            "name": name,
            "include_in_schema": include_in_schema,
            "openapi_extra": openapi_extra,
            "status_code": status_code,
        }
        return wraps(func)(lambda *args, **kwargs: func(*args, **kwargs))
    return decorator

# Global storage for API routers
API_ROUTERS: Dict[str, APIRouter] = {}

class URL_PATH_STORE:
    """Class for storing URL paths with optimized memory usage"""
    __slots__ = ('value',)
    def __init__(self, init: Any):
        self.value = init

# Registry for storing action paths and their corresponding functions
actionRegistry = URL_PATH_STORE([])

@lru_cache(maxsize=128)
def _generate_action_paths(func_name: str, slug: Optional[List[str]]) -> tuple[str, str]:
    """
    Generate URL paths for actions with caching.
    Args:
        func_name: Name of the function
        slug: Optional URL path segments
    Returns:
        Tuple of (server path, client-side JS path)
    """
    hash_input = f"{func_name}_{'-'.join(slug) if slug else ''}"
    action_id = hashlib.md5(hash_input.encode()).hexdigest()[:64]
    slug_path = "/".join(f"{{{s}}}" for s in slug) if slug else ""
    slug_pathjs = "/".join(f"${{slugs?.{s}}}" for s in slug) if slug else ""
    return (
        f"/{action_id}/{slug_path}".rstrip("/"),
        f"/{action_id}/{slug_pathjs}".rstrip("/")
    )

def action(slug: Optional[List[str]] = None):
    """
    Decorator for registering server actions.
    
    Args:
        slug: Optional list of URL path segments
    """
    def decorator(func: Callable) -> Callable:
        # Generate unique paths for the action
        path, pathjs = _generate_action_paths(func.__name__, slug)
        func.action_path = path

        # Get the module path for the action
        frame = inspect.currentframe()
        module_path = None
        if frame and frame.f_back:
            full_path = inspect.getmodule(frame.f_back).__file__
            project_name = Path.cwd().name
            module_path = full_path.split(project_name)[-1].replace('.py', '.js').replace('\\', '/')

        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Handle both async and sync functions
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)

        # Generate client-side JavaScript code
        params = {k: v for k, v in func.__annotations__.items() if v is not Request}
        generate_js_action(func_name=func.__name__, path=module_path, url=pathjs, params=params, slug=slug)
        actionRegistry.value.append({"path": path, "func": wrapper})
        
        return wrapper
    return decorator
