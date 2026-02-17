import inspect
from typing import Any, Type, List, Dict, Set, Iterable, Callable
from fastapi import APIRouter, Depends
from threading import RLock

HTTP_METHODS: Set[str] = {"GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"}

# --- 1. DÉCORATEUR INJECTABLE (Doit être défini avant le Container pour référence) ---
def Injectable():
    """Marque une classe comme service injectable"""
    def wrapper(cls):
        cls.__injectable__ = True
        return cls
    return wrapper

# --- 2. SYSTEME D'INJECTION (CONTAINER INTELLIGENT) ---


class Container:
    _instances: Dict[Type, Any] = {}
    _lock = RLock()
    # On suit les classes en cours de résolution pour détecter les boucles infinies
    _resolving: Set[Type] = set()

    @classmethod
    def resolve(cls, target_cls: Type):
        # 1. Accès rapide (Fast path) sans verrou
        if target_cls in cls._instances:
            return cls._instances[target_cls]

        with cls._lock:
            # 2. Double-check locking
            if target_cls in cls._instances:
                return cls._instances[target_cls]

            # 3. Détection de cycle (Dépendances circulaires)
            if target_cls in cls._resolving:
                raise RecursionError(f"Cycle détecté pour {target_cls.__name__}")
            
            cls._resolving.add(target_cls)
            try:
                # 4. Résolution simplifiée
                init = target_cls.__init__
                if init is object.__init__:
                    instance = target_cls()
                else:
                    deps = []
                    params = inspect.signature(init).parameters
                    for name, param in params.items():
                        if name == "self":
                            continue
                        dep_type = param.annotation
                        if hasattr(dep_type, "__injectable__"):
                            deps.append(cls.resolve(dep_type))
                        elif param.default is inspect.Parameter.empty:
                            raise ValueError(f"Dépendance {name}: {dep_type} non injectable dans {target_cls.__name__}")
                    
                    instance = target_cls(*deps)

                cls._instances[target_cls] = instance
                return instance
            finally:
                cls._resolving.remove(target_cls)

# --- 3. AUTRES DÉCORATEURS ---

def Controller(prefix: str = "", tags: List[str] = None):
    def wrapper(cls):
        cls.__is_controller__ = True
        cls.__controller_prefix__ = prefix
        cls.__controller_tags__ = tags or [cls.__name__]
        return cls
    return wrapper


def UseGuard(*guards: Callable[..., Any]):
    def wrapper(target: Any) -> Any:
        existing = getattr(target, "__nexy_guards__", ())
        target.__nexy_guards__ = tuple(existing) + tuple(guards)
        return target
    return wrapper


def UseMiddleware(*middlewares: Callable[..., Any]):
    def wrapper(target: Any) -> Any:
        existing = getattr(target, "__nexy_middlewares__", ())
        target.__nexy_middlewares__ = tuple(existing) + tuple(middlewares)
        return target
    return wrapper

def Module(
    controllers: List[Type],
    providers: List[Type] = [], # Devenu Optionnel
    imports: List[APIRouter] = None,
    prefix: str = ""
):

    def wrapper(cls):
        # Validation allégée : on exige seulement des controllers
        if not controllers:
            raise ValueError(f"Module {cls.__name__} doit avoir au moins un controller")
        
        module_router = APIRouter(prefix=prefix)
        
        # 1. Pré-chargement explicite (Optionnel mais utile pour forcer l'instanciation)
        # Même si on ne les met pas ici, Container.resolve les trouvera quand même via le Controller
        for provider_cls in providers:
            if not hasattr(provider_cls, '__injectable__'):
                raise ValueError(f"{provider_cls.__name__} doit être @Injectable()")
            Container.resolve(provider_cls)
        
        # 2. Imports sous-modules
        if imports:
            for sub_router in imports:
                module_router.include_router(sub_router)
        
        # 3. Enregistrement des contrôleurs
        # C'est ici que la chaîne d'injection démarre
        for ctrl_cls in controllers:
            _register_controller(ctrl_cls, module_router)
        
        return module_router
    return wrapper

def _register_controller(ctrl_cls: Type, parent_router: APIRouter):
    ctrl_prefix = getattr(ctrl_cls, '__controller_prefix__', '')
    ctrl_tags = getattr(ctrl_cls, '__controller_tags__', [])
    ctrl_router = APIRouter(prefix=ctrl_prefix, tags=ctrl_tags)
    
    # ICI : Container.resolve va analyser le Controller, voir qu'il a besoin d'un Service,
    # vérifier si le Service est @Injectable, et le créer à la volée.
    ctrl_instance = Container.resolve(ctrl_cls)
    class_guards: Iterable[Callable[..., Any]] = getattr(ctrl_cls, "__nexy_guards__", ())
    class_middlewares: Iterable[Callable[..., Any]] = getattr(ctrl_cls, "__nexy_middlewares__", ())
    seen_http_methods: Set[str] = set()
    for method_name, method_func in inspect.getmembers(ctrl_instance, predicate=inspect.ismethod):
        method_upper = method_name.upper()
        if method_upper in HTTP_METHODS:
            if method_upper in seen_http_methods:
                raise ValueError(f"Controller {ctrl_cls.__name__} has multiple handlers for HTTP method {method_upper}")
            seen_http_methods.add(method_upper)
            method_guards: Iterable[Callable[..., Any]] = getattr(method_func, "__nexy_guards__", ())
            method_middlewares: Iterable[Callable[..., Any]] = getattr(method_func, "__nexy_middlewares__", ())
            dependencies = [
                Depends(dep)
                for dep in (
                    *class_guards,
                    *class_middlewares,
                    *method_guards,
                    *method_middlewares,
                )
            ]
            ctrl_router.add_api_route(
                path="/",
                endpoint=method_func,
                methods=[method_upper],
                name=f"{ctrl_cls.__name__}.{method_name}",
                dependencies=dependencies or None,
            )
        elif method_upper == "SOCKET":
            ctrl_router.add_api_websocket_route(path="/", endpoint=method_func)
    
    parent_router.include_router(ctrl_router)
