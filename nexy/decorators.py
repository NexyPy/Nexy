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
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, Union
from pathlib import Path

# Import FastAPI related dependencies
from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi import APIRouter, Depends, Request 
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse
from fastapi.types import IncEx

from jinja2 import Environment, Template

from nexy.hooks import useView
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

template_cache = {}

def use(func: Callable) -> str:
    """
    Get the action path for a decorated function.
    
    Args:
        func: Function decorated with @action
    
    Returns:
        Action path as string
    
    Raises:
        ValueError: If function is not decorated with @action
    """
    if not hasattr(func, 'action_path'):
        raise ValueError("Function is not a server action (missing @action decorator)")
    return f"use('{func.action_path}')"


def component(*, imports: Optional[List[Any]] = None):
    def decorator(func: Union[Callable, Type]) -> Union[Callable, Type]:
        
        def get_context():
            """Build and return the rendering context from provided imports and 'use'."""
            base_imports = (imports.copy() if imports else [])
            base_imports.append(use)
            return {imp.__name__: imp for imp in base_imports}
        
        def load_file_content(file_path: Path, tag: str) -> str:
            """Load file content, remove newlines/tabs, and wrap in the specified HTML tag."""
            if not file_path.exists():
                return ""
            content = file_path.read_text(encoding='utf-8')
            content = re.sub(r'\s+', ' ', content).strip()
            return f"<{tag}>{content}</{tag}>"
        
        def parse_attributes(attr_str: str) -> List[str]:
            """
            Parse attributes from a string.
            Matches key="value", key='value', or key=value (without spaces in value).
            """
            return re.findall(r'(\w+=(?:"[^"]*"|\'[^\']*\'|\S+))', attr_str)
        
        def construct_html(module_path: Path, obj_name: str, result: Any, kwargs: dict) -> str:
            # Build file paths.
            template_path = module_path / f"{obj_name}.html"
            style_path = module_path / f"{obj_name}.css"
            script_path = module_path / f"{obj_name}.js"
            
            if not template_path.exists():
                raise ValueError(f"Template file not found: {template_path}")
            
            html_content = template_path.read_text(encoding='utf-8')
            style_content = load_file_content(style_path, "style type='text/css' class='scoped-style'")
            script_content = load_file_content(script_path, "script type='module' async defer")
            
            def replace_standard(match):
                tag_name = match.group(1)
                attrs = match.group(2).strip()
                children = match.group(3).strip()
                
                parsed_attrs = parse_attributes(attrs) if attrs else []
                attr_str = ", ".join(parsed_attrs)
                return f"{{% call {tag_name}({attr_str}) %}}{children}{{% endcall %}}"
            
            html_content = re.sub(
                r'<([A-Z][a-zA-Z0-9]*)\b([^>]*)>(.*?)<\/\1>',
                replace_standard,
                html_content,
                flags=re.DOTALL
            )
            
            # Replace self-closing component tags, e.g. <MyComponent attr="value" />
            def replace_self_closing(match):
                tag_name = match.group(1)
                attrs = match.group(2).strip()
                parsed_attrs = parse_attributes(attrs) if attrs else []
                attr_str = ", ".join(parsed_attrs)
                if attr_str:
                    return f"{{{{ {tag_name}({attr_str}) }}}}"
                return f"{{{{ {tag_name}() }}}}"
            
            html_content = re.sub(
                r'<([A-Z][a-zA-Z0-9]*)\b([^>]*)\/>',
                replace_self_closing,
                html_content
            )
            
            return re.sub(r'[\n\t]', '', f"{style_content}{script_content}{html_content}".replace("nexy:","/nexy_public/"))
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Validate module
            module = inspect.getmodule(func)
            if module is None or not hasattr(module, '__file__'):
                raise ValueError("Could not determine module for function")
            module_path = Path(module.__file__).resolve().parent
            
            base_context = get_context()
            result = func(*args, **kwargs)
            
            def render_result(data):
                # Generate HTML from template
                raw_html = construct_html(module_path, func.__name__, data, kwargs)
                tmpl = Template(raw_html)
                
                # Build render context
                render_context = {
                    **base_context,
                    **(data if isinstance(data, dict) else kwargs)
                }
                
                # Special handling for View components
                if func.__name__ == "View":
                    code = tmpl.render(**render_context)
                    path = str(module_path)
                    path = "app" + (path.split("app", 1)[1] if "app" in path else path)
                    return useView(code=code, path=path)
                
                return tmpl.render(**render_context)
            
            # Handle async or sync response
            if inspect.isawaitable(result):
                async def async_wrapper():
                    data = await result
                    return render_result(data)
                return async_wrapper()
            
            return render_result(result)
            
        return wrapper
    return decorator

