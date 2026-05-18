import functools
import inspect
from collections.abc import Callable, Iterable, Mapping
from contextvars import ContextVar
from enum import Enum
from threading import RLock
from typing import AbstractSet, Any

from fastapi import APIRouter, Depends
from fastapi.responses import Response

from nexy.routers.actions.store import ACTIONS_STORE

HTTP_METHODS: set[str] = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}


class Scope(Enum):
    SINGLETON = "singleton"
    REQUEST = "request"
    TRANSIENT = "transient"


def Injectable(scope: Scope = Scope.SINGLETON) -> Callable[[type[Any]], type[Any]]:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.__injectable__ = True
        cls.__injectable_scope__ = scope

        if cls.__init__ is not object.__init__:
            original_init = cls.__init__

            @functools.wraps(original_init)
            def _guarded_init(self, *args: Any, **kwargs: Any) -> None:
                if not Container._di_context.get():
                    raise TypeError(
                        f"{cls.__name__} is managed by Nexy. "
                        f"Use Container.resolve() or inject it via another service/controller."
                    )
                original_init(self, *args, **kwargs)

            cls.__init__ = _guarded_init

        return cls

    return wrapper


class Container:
    _instances: dict[type[Any], Any] = {}
    _lock = RLock()
    _resolving: set[type[Any]] = set()
    _request_store: ContextVar = ContextVar("_request_store", default=None)
    _di_context: ContextVar[bool] = ContextVar("_di_context", default=False)

    @classmethod
    def resolve(cls, target_cls: type[Any]) -> Any:
        scope = getattr(target_cls, "__injectable_scope__", Scope.SINGLETON)

        if scope == Scope.REQUEST:
            return cls._resolve_request(target_cls)
        if scope == Scope.TRANSIENT:
            return cls._create(target_cls)

        return cls._resolve_singleton(target_cls)

    @classmethod
    def _resolve_singleton(cls, target_cls: type[Any]) -> Any:
        if target_cls in cls._instances:
            return cls._instances[target_cls]

        with cls._lock:
            if target_cls in cls._instances:
                return cls._instances[target_cls]
            instance = cls._create(target_cls)
            cls._instances[target_cls] = instance
            return instance

    @classmethod
    def _resolve_request(cls, target_cls: type[Any]) -> Any:
        store = cls._request_store.get()
        if store is None:
            store = {}
        if target_cls not in store:
            store[target_cls] = cls._create(target_cls)
            cls._request_store.set(store)
        return store[target_cls]

    @classmethod
    def clear_request_scope(cls) -> None:
        cls._request_store.set(None)

    @classmethod
    def _create(cls, target_cls: type[Any]) -> Any:
        if target_cls in cls._resolving:
            raise RecursionError(f"Cycle detected for {target_cls.__name__}")

        cls._resolving.add(target_cls)
        try:
            if "__init__" not in target_cls.__dict__:
                return target_cls()

            deps: list[Any] = []
            init = target_cls.__init__
            for name, param in inspect.signature(init).parameters.items():
                if name == "self":
                    continue
                dep_type = param.annotation
                if hasattr(dep_type, "__injectable__"):
                    deps.append(cls.resolve(dep_type))
                elif param.default is inspect.Parameter.empty:
                    raise ValueError(
                        f"Dependency {name}: {dep_type} is not injectable in {target_cls.__name__}"
                    )

            token = cls._di_context.set(True)
            try:
                instance = target_cls(*deps)
            finally:
                cls._di_context.reset(token)
            return instance
        finally:
            cls._resolving.discard(target_cls)


# --- 3. OTHER DECORATORS ---


def Controller(prefix: str = "", tags: list[str] | None = None) -> Callable[[type[Any]], type[Any]]:
    def wrapper(cls: type[Any]) -> type[Any]:
        cls.__is_controller__ = True
        cls.__controller_prefix__ = prefix
        cls.__controller_tags__ = tags or [cls.__name__]
        return cls

    return wrapper


def UseGuard(*guards: Callable[..., Any]) -> Callable[[Any], Any]:
    def wrapper(target: Any) -> Any:
        existing = getattr(target, "__nexy_guards__", ())
        target.__nexy_guards__ = tuple(existing) + tuple(guards)
        return target

    return wrapper


def Middleware(*middlewares: Callable[..., Any]) -> Callable[[Any], Any]:
    def wrapper(target: Any) -> Any:
        existing = getattr(target, "__nexy_middlewares__", ())
        target.__nexy_middlewares__ = tuple(existing) + tuple(middlewares)
        return target

    return wrapper


class RouteMeta:
    def __init__(
        self,
        name: str | None = None,
        tags: list[str] | None = None,
        summary: str | None = None,
        description: str | None = None,
        deprecated: bool | None = None,
        include_in_schema: bool | None = None,
        operation_id: str | None = None,
        openapi_extra: dict[str, Any] | None = None,
    ) -> None:
        self.name = name
        self.tags = tags
        self.summary = summary
        self.description = description
        self.deprecated = deprecated
        self.include_in_schema = include_in_schema
        self.operation_id = operation_id
        self.openapi_extra = openapi_extra


class ResponseMeta:
    def __init__(
        self,
        status_code: int | None = None,
        response_class: type[Response] | None = None,
        response_model: type[Any] | None = None,
        responses: dict[int | str, Any] | None = None,
        response_description: str | None = None,
        response_model_include: AbstractSet[str] | Mapping[str, Any] | None = None,
        response_model_exclude: AbstractSet[str] | Mapping[str, Any] | None = None,
        response_model_by_alias: bool | None = None,
        response_model_exclude_unset: bool | None = None,
        response_model_exclude_defaults: bool | None = None,
        response_model_exclude_none: bool | None = None,
    ) -> None:
        self.status_code = status_code
        self.response_class = response_class
        self.response_model = response_model
        self.responses = responses
        self.response_description = response_description
        self.response_model_include = response_model_include
        self.response_model_exclude = response_model_exclude
        self.response_model_by_alias = response_model_by_alias
        self.response_model_exclude_unset = response_model_exclude_unset
        self.response_model_exclude_defaults = response_model_exclude_defaults
        self.response_model_exclude_none = response_model_exclude_none


def UseRoute(
    name: str | None = None,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    deprecated: bool | None = None,
    include_in_schema: bool | None = None,
    operation_id: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    meta = RouteMeta(
        name=name,
        tags=tags,
        summary=summary,
        description=description,
        deprecated=deprecated,
        include_in_schema=include_in_schema,
        operation_id=operation_id,
        openapi_extra=openapi_extra,
    )

    def wrapper(handler: Callable[..., Any]) -> Callable[..., Any]:
        handler.__nexy_route_meta__ = meta
        return handler

    return wrapper


def useRoute(
    name: str | None = None,
    tags: list[str] | None = None,
    summary: str | None = None,
    description: str | None = None,
    deprecated: bool | None = None,
    include_in_schema: bool | None = None,
    operation_id: str | None = None,
    openapi_extra: dict[str, Any] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    return UseRoute(
        name=name,
        tags=tags,
        summary=summary,
        description=description,
        deprecated=deprecated,
        include_in_schema=include_in_schema,
        operation_id=operation_id,
        openapi_extra=openapi_extra,
    )


def UseResponse(
    status_code: int | None = None,
    response_class: type[Response] | None = None,
    response_model: type[Any] | None = None,
    responses: dict[int | str, Any] | None = None,
    response_description: str | None = None,
    response_model_include: AbstractSet[str] | Mapping[str, Any] | None = None,
    response_model_exclude: AbstractSet[str] | Mapping[str, Any] | None = None,
    response_model_by_alias: bool | None = None,
    response_model_exclude_unset: bool | None = None,
    response_model_exclude_defaults: bool | None = None,
    response_model_exclude_none: bool | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    meta = ResponseMeta(
        status_code=status_code,
        response_class=response_class,
        response_model=response_model,
        responses=responses,
        response_description=response_description,
        response_model_include=response_model_include,
        response_model_exclude=response_model_exclude,
        response_model_by_alias=response_model_by_alias,
        response_model_exclude_unset=response_model_exclude_unset,
        response_model_exclude_defaults=response_model_exclude_defaults,
        response_model_exclude_none=response_model_exclude_none,
    )

    def wrapper(handler: Callable[..., Any]) -> Callable[..., Any]:
        handler.__nexy_response_meta__ = meta
        return handler

    return wrapper


def Module(
    prefix: str = "",
) -> Callable[[type[Any]], APIRouter]:
    def wrapper(cls: type[Any]) -> APIRouter:
        controllers_list = getattr(cls, "controllers", [])
        providers_list = getattr(cls, "providers", [])
        imports_list = getattr(cls, "imports", [])
        exports_list = getattr(cls, "exports", [])
        if not controllers_list:
            raise ValueError(f"Module {cls.__name__} must have at least one controller")

        module_router = APIRouter(prefix=prefix)
        module_router.__module_exports__ = exports_list

        for sub_router in imports_list:
            for exported_cls in getattr(sub_router, "__module_exports__", []):
                if hasattr(exported_cls, "__injectable__"):
                    Container.resolve(exported_cls)

        for provider_cls in providers_list:
            if not hasattr(provider_cls, "__injectable__"):
                raise ValueError(f"{provider_cls.__name__} must be @Injectable()")
            Container.resolve(provider_cls)

        if imports_list:
            for sub_router in imports_list:
                module_router.include_router(sub_router)

        for ctrl_cls in controllers_list:
            _register_controller(ctrl_cls, module_router)

        return module_router

    return wrapper


def _register_controller(ctrl_cls: type[Any], parent_router: APIRouter) -> None:
    ctrl_prefix = getattr(ctrl_cls, "__controller_prefix__", "")
    path_tag = parent_router.prefix + ctrl_prefix if (parent_router.prefix or ctrl_prefix) else "/"
    ctrl_router = APIRouter(prefix=ctrl_prefix, tags=[path_tag])

    # Container.resolve analyzes the Controller, resolves its Service dependency
    ctrl_instance = Container.resolve(ctrl_cls)
    class_guards: Iterable[Callable[..., Any]] = getattr(ctrl_cls, "__nexy_guards__", ())
    class_middlewares: Iterable[Callable[..., Any]] = getattr(ctrl_cls, "__nexy_middlewares__", ())
    seen_http_methods: set[str] = set()
    for method_name, method_func in inspect.getmembers(ctrl_instance, predicate=inspect.ismethod):
        method_upper = method_name.upper()
        if method_upper in HTTP_METHODS:
            if method_upper in seen_http_methods:
                print(f"{ctrl_cls.__name__} has multiple handlers for HTTP method {method_upper} ")
                raise ValueError(
                    f"Controller {ctrl_cls.__name__} has multiple handlers for HTTP method {method_upper}"
                )
            seen_http_methods.add(method_upper)
            method_guards: Iterable[Callable[..., Any]] = getattr(
                method_func, "__nexy_guards__", ()
            )
            method_middlewares: Iterable[Callable[..., Any]] = getattr(
                method_func, "__nexy_middlewares__", ()
            )
            dependencies = [
                Depends(dep)
                for dep in (
                    *class_guards,
                    *class_middlewares,
                    *method_guards,
                    *method_middlewares,
                )
            ]
            route_meta: RouteMeta | None = getattr(method_func, "__nexy_route_meta__", None)
            response_meta: ResponseMeta | None = getattr(
                method_func, "__nexy_response_meta__", None
            )
            route_name = f"{ctrl_cls.__name__}.{method_name}"
            if route_meta is not None and route_meta.name:
                route_name = route_meta.name
            route_kwargs: dict[str, Any] = {
                "path": "/",
                "endpoint": method_func,
                "methods": [method_upper],
                "name": route_name,
                "dependencies": dependencies or None,
            }
            if route_meta is not None and route_meta.tags is not None:
                route_kwargs["tags"] = route_meta.tags
            if response_meta is not None:
                if response_meta.status_code is not None:
                    route_kwargs["status_code"] = response_meta.status_code
                if response_meta.response_class is not None:
                    route_kwargs["response_class"] = response_meta.response_class
                if response_meta.response_model is not None:
                    route_kwargs["response_model"] = response_meta.response_model
                if response_meta.responses is not None:
                    route_kwargs["responses"] = response_meta.responses
                if response_meta.response_description is not None:
                    route_kwargs["response_description"] = response_meta.response_description
                if response_meta.response_model_include is not None:
                    route_kwargs["response_model_include"] = response_meta.response_model_include
                if response_meta.response_model_exclude is not None:
                    route_kwargs["response_model_exclude"] = response_meta.response_model_exclude
                if response_meta.response_model_by_alias is not None:
                    route_kwargs["response_model_by_alias"] = response_meta.response_model_by_alias
                if response_meta.response_model_exclude_unset is not None:
                    route_kwargs["response_model_exclude_unset"] = (
                        response_meta.response_model_exclude_unset
                    )
                if response_meta.response_model_exclude_defaults is not None:
                    route_kwargs["response_model_exclude_defaults"] = (
                        response_meta.response_model_exclude_defaults
                    )
                if response_meta.response_model_exclude_none is not None:
                    route_kwargs["response_model_exclude_none"] = (
                        response_meta.response_model_exclude_none
                    )
            ctrl_router.add_api_route(**route_kwargs)
        elif method_upper == "SOCKET":
            ctrl_router.add_api_websocket_route(path="/", endpoint=method_func)

    parent_router.include_router(ctrl_router)


def Action(func: Callable | None = None):
    def decorator(f: Callable):
        ACTIONS_STORE.register(f)
        return f

    if func is None:
        return decorator

    return decorator(func)


def Task(func: Callable | None = None):
    pass


def Job(func: Callable | None = None):
    pass
