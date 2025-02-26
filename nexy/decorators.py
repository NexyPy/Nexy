"""
Author: Espoir Loém

This module provides various decorators for use in the Nexy framework, including dependency injection,
HTTP response handling, and component rendering.
"""

import asyncio
from functools import wraps
import inspect
import re
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, TypeVar, Union
import uuid
from pathlib import Path

from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi import APIRouter, Depends 
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.datastructures import Default
from fastapi.types import IncEx
from jinja2 import Environment, Template

from nexy.hooks import useView

T = TypeVar("T")
DependencyType = Union[Callable[..., Any], Type[Any]]

def Injectable() -> Any:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return Depends(result)
        return wrapper
    return decorator

def Inject(dependencies: Sequence[Depends] | None = None):
    def decorator(func):
        func.params = {
            "dependencies": dependencies,
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper
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
        type: type[FastAPIResponse] | DefaultPlaceholder = Default(JSONResponse), # type: ignore
         ):
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
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def Describe(
      summary: str | None = None,
      description: str | None = None,
      response: str = "Successful Response",
      ):
    def decorator(func):
        func.params = {
            "summary": summary,
            "description": description,
            "response_description": response,
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

def Config(
        status_code: int | None = None,
        deprecated: bool | None = None,
        operation_id: str | None = None,
        include_in_schema: bool = True,
        name: str | None = None,
        openapi_extra: Dict[str, Any] | None = None,
        ):
    def decorator(func):
        func.params = {
            "deprecated": deprecated,
            "operation_id": operation_id,
            "name": name,
            "include_in_schema": include_in_schema,
            "openapi_extra": openapi_extra,
            "status_code": status_code,
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

API_ROUTERS: Dict[str, APIRouter] = {}

class Controller:
    def __init__(self, path: str = ""):
        self.path = path

    def __call__(self, cls):
        router = APIRouter(prefix=self.path)
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if callable(attr) and hasattr(attr, "route_info"):
                method, route_path = attr.route_info
                router.add_api_route(route_path, attr, methods=[method])
        API_ROUTERS[self.path] = router
        return cls

def Get(path: str):
    def decorator(func):
        func.route_info = ("GET", path)
        return func
    return decorator

def Post(path: str):
    def decorator(func):
        func.route_info = ("POST", path)
        return func
    return decorator

def Put(path: str):
    def decorator(func):
        func.route_info = ("PUT", path)
        return func
    return decorator

def Delete(path: str):
    def decorator(func):
        func.route_info = ("DELETE", path)
        return func
    return decorator

class ActionStore:
    def __init__(self, init: Any):
        self.value = init

# Global action registry
actionRegistry = ActionStore([])

def Action(slug: Optional[List[str]] = None):
    """
    Decorator for registering server actions.
    
    Args:
        slug: Optional list of URL path segments
    """
    def decorator(func: Callable) -> Callable:
        action_id = str(uuid.uuid4())
        slug_path = "/".join(f"{{{s}}}" for s in slug) if slug else ""
        path = f"/{action_id}/{slug_path}".rstrip("/")

        # Store the path in function attributes for reference
        func.action_path = path
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            return func(*args, **kwargs)
        
        actionRegistry.value.append({"path": path, "func": wrapper})
        
        return wrapper
    return decorator

def view(func: Callable) -> Callable:
    def get_layout_content(module_path: Path) -> str:
        """
        Recursively find and load layout content from parent directories.
        """
        layout_content = ""
        current_path = module_path
        while current_path != current_path.parent:
            layout_file = current_path / "layout.html"
            if layout_file.exists():
                layout_content = "" #load_file_content(layout_file, "div") + layout_content
            current_path = current_path.parent
        return layout_content

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        module = inspect.getmodule(func)
        if module is None or not hasattr(module, '__file__'):
            raise ValueError("Could not determine module for function")
        module_path = Path(module.__file__).parent

        result = func(*args, **kwargs)
        layout_content = get_layout_content(module_path)
        
        if isinstance(result, dict):
            result["layout"] = layout_content
        else:
            result = {"content": result, "layout": layout_content}
        
        return result

    wrapper.isView = True
    return wrapper

def layout(func: Callable) -> Callable:
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return func(*args, **kwargs)
    wrapper.isLayout = True
    return wrapper

# Cache for templates
template_cache = {}

def get_environment() -> Environment:
    return Environment(
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True
    )

def Component(*, imports: Optional[List[Any]] = None):
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
            content = re.sub(r'[\n\t]', '', content)
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
            script_content = load_file_content(script_path, "script type='module' async class='scoped-script '")
            
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
            
            return re.sub(r'[\n\t]', '', f"{style_content}{script_content}{html_content}")
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



