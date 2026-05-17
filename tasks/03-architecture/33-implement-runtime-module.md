# Task 33: Implement runtime module

## Problem

All files in `nexy/runtime/` are empty stubs:
- `__init__.py` — empty
- `main.py` — empty
- `injection.py` — empty (referenced by `AGENTS.md` as `nexy/runtime/injection.py` for DI)
- `renderer.py` — empty
- `router.py` — empty

The `AGENTS.md` says: *"Depend on abstractions (`Protocol`), inject via `nexy/runtime/injection.py`"* — this module needs to exist.

## Implementation

### 1. `nexy/runtime/__init__.py`

```python
"""Nexy runtime — DI container, renderer, and client-side router abstractions."""
```

### 2. `nexy/runtime/injection.py`

Simple DI container using `Protocol` for abstraction (per AGENTS.md):

```python
from typing import Any, TypeVar, Generic
from dataclasses import dataclass, field

T = TypeVar("T")

class ServiceProvider:
    """Simple service provider / DI container.
    
    Usage:
        provider = ServiceProvider()
        provider.register(MyService, lambda: MyService())
        service = provider.resolve(MyService)
    """
    def __init__(self) -> None:
        self._services: dict[type, Any] = {}
        self._factories: dict[type, callable] = {}

    def register(self, cls: type, factory: callable | None = None) -> None:
        self._factories[cls] = factory or cls

    def resolve(self, cls: type[T]) -> T:
        if cls in self._services:
            return self._services[cls]
        factory = self._factories.get(cls)
        if factory is None:
            raise KeyError(f"No provider registered for {cls.__name__}")
        instance = factory()
        self._services[cls] = instance
        return instance

    def singleton(self, cls: type, instance: Any) -> None:
        self._services[cls] = instance
```

### 3. `nexy/runtime/renderer.py`

```python
"""Server-side renderer abstraction."""
from dataclasses import dataclass
from typing import Any

@dataclass
class RenderContext:
    request: Any | None = None
    props: dict[str, Any] | None = None
    slots: dict[str, str] | None = None

class Renderer:
    """Base renderer. Framework-specific renderers extend this."""
    def render(self, component: str, context: RenderContext | None = None) -> str:
        raise NotImplementedError
```

### 4. `nexy/runtime/router.py`

```python
"""Client-side router for SPA navigation."""
from dataclasses import dataclass
from typing import Callable

class ClientRouter:
    """Minimal client-side router for SPA navigation."""
    _routes: dict[str, Callable] = {}
    
    @classmethod
    def register(cls, path: str, handler: Callable) -> None:
        cls._routes[path] = handler
    
    @classmethod
    def navigate(cls, path: str) -> None:
        handler = cls._routes.get(path)
        if handler:
            handler()
```

### 5. `nexy/runtime/main.py`

```python
"""Runtime initialization."""
from nexy.runtime.injection import ServiceProvider

_runtime_provider = ServiceProvider()

def get_provider() -> ServiceProvider:
    return _runtime_provider
```

## Search commands

```bash
rg "from nexy\.runtime" nexy/ tests/
# Confirm all runtime files exist:
Get-ChildItem -Path "nexy/runtime" -Filter "*.py"
```

## Verify

- [ ] `nexy/runtime/injection.py` exists and has `ServiceProvider` class
- [ ] `nexy/runtime/renderer.py` exists and has `Renderer` + `RenderContext`
- [ ] `nexy/runtime/router.py` exists and has `ClientRouter`
- [ ] `nexy/runtime/main.py` exists and has `get_provider()`
- [ ] `python -c "from nexy.runtime.injection import ServiceProvider"` works
- [ ] `ruff check nexy/` — no lint errors
- [ ] `python -m mypy nexy --strict` — no type errors
