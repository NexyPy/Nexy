from collections.abc import Callable
from typing import Any

from fastapi import Depends


class RouteMiddleware:
    @staticmethod
    def resolve(handler: Callable[..., Any]) -> list[Depends]:
        """Extracts guards and middlewares attached to a handler function."""
        guards = getattr(handler, "__nexy_guards__", ())
        middlewares = getattr(handler, "__nexy_middlewares__", ())

        # Combine all callables
        all_callables = [*guards, *middlewares]
        return [Depends(dep) for dep in all_callables]
