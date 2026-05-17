# Task 36: Improve router modular structure

## Problem

Two areas violate the project's SOLID/KISS principles:

1. `nexy/routers/fbrouter/__init__.py:FBRouter._register_all_routes()` (~45 lines) — too long, does multiple things (handles API vs Component routes, dep collection, validation, metadata extraction)

2. `nexy/decorators.py:_register_controller()` (~70+ lines) — violates the `< 20 lines per function` rule, handles too many concerns

3. `nexy/routers/actions/` is the only well-structured sub-module with clear separation (Engine/Store)

## Changes

### 1. Extract route registration from `FBRouter`

Create `nexy/routers/fbrouter/registration.py`:

```python
"""Route registration logic — extracted from FBRouter for SOLID compliance."""
from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from typing import Any

from nexy.routers.fbrouter.dependencies import RouteDependencies
from nexy.routers.fbrouter.middleware import RouteMiddleware
from nexy.routers.fbrouter.validator import RouteValidator

HTTP_METHODS_MAP = {
    "GET": "get", "POST": "post", "PUT": "put",
    "DELETE": "delete", "PATCH": "patch",
    "OPTIONS": "options", "HEAD": "head",
}

def register_api_route(router: APIRouter, module: Any, path: str, source: str) -> None:
    folder_deps = [Depends(d) for d in RouteDependencies.collect(source)]
    for method, _ in HTTP_METHODS_MAP.items():
        if handler := getattr(module, method, None):
            RouteValidator.validate_sig(handler, path, method)
            deps = RouteMiddleware.resolve(handler) + folder_deps
            r_meta = getattr(handler, "__nexy_route_meta__", None)
            resp_meta = getattr(handler, "__nexy_response_meta__", None)
            router.add_api_route(
                path=path, endpoint=handler, methods=[method],
                dependencies=deps or None, name=method, tags=[path],
                status_code=resp_meta.status_code if resp_meta else None,
            )
    if ws_handler := getattr(module, "SOCKET", None):
        router.websocket(path)(ws_handler)


def register_component_route(router: APIRouter, module: Any, path: str, source: str, comp_name: str) -> None:
    folder_deps = [Depends(d) for d in RouteDependencies.collect(source)]
    if component := getattr(module, comp_name, None):
        router.get(
            path, response_class=HTMLResponse,
            dependencies=folder_deps or None,
            name=component.__name__,
            description=component.__doc__ or "",
            tags=[path],
        )(component)
```

### 2. Simplify `FBRouter._register_all_routes`

```python
# Before: ~45 lines with nested conditionals
def _register_all_routes(self):
    for meta in self.modules_meta:
        # ... 45 lines of inline logic

# After: ~10 lines, delegating to specialized functions
def _register_all_routes(self) -> None:
    for meta in self.modules_meta:
        if meta["type"] == "api":
            register_api_route(self.router, meta["module"], meta["pathname"], meta["source"])
        else:
            register_component_route(self.router, meta["module"], meta["pathname"], meta["source"], meta["comp_name"])
```

### 3. Extract controller registration from `decorators.py`

Move `_register_controller()` to `nexy/routers/registration.py`:

```python
def register_controller(ctrl_cls: type, parent_router: APIRouter) -> None:
    """Register a @Controller-decorated class on the parent router."""
    # ... extracted from decorators.py:_register_controller
```

Then in `decorators.py`, import and use:
```python
from nexy.routers.registration import register_controller

def Module(prefix: str = "") -> Callable[[type], APIRouter]:
    def wrapper(cls: type) -> APIRouter:
        # ...
        for ctrl_cls in controllers_list:
            register_controller(ctrl_cls, module_router)
        return module_router
    return wrapper
```

## Verify commands

```bash
rg "_register_all_routes" nexy/
rg "_register_controller" nexy/
rg "def _register" nexy/
```

## Verify

- [ ] `_register_all_routes()` is ≤ 15 lines
- [ ] `register_api_route()` and `register_component_route()` each handle one responsibility
- [ ] `_register_controller()` moved out of `decorators.py` (or kept but simplified to < 20 lines)
- [ ] All existing route functionality preserved
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m pytest tests/ -v` — no regressions
