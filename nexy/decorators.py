
from functools import wraps
from typing import Any, Callable, Dict, Optional, Sequence, Type, TypeVar, Union

from fastapi.datastructures import Default, DefaultPlaceholder
from fastapi import Depends 
from fastapi import Response as FastAPIResponse
from fastapi.responses import JSONResponse 
from fastapi.datastructures import Default
from fastapi.types import IncEx





T = TypeVar("T")
DependencyType = Union[Callable[..., Any], Type[Any]]

def Injectable() -> Any:
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Appeler la fonction originale et obtenir son résultat
            result = func(*args, **kwargs)
            return Depends(result)
        return wrapper
    return decorator



def Inject(dependencies:Sequence[Depends] | None = None):
    def decorator(func):
        func.params = {
            "dependencies": dependencies,
        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Appeler la fonction originale et obtenir son résultat
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorator



def CustomResponse(
        model:Any = Default(None),
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
            # Appeler la fonction originale et obtenir son résultat
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorator


def Describe(
      summary: str | None = None,
      decription: str | None = None,
      response: str = "Successful Response",
      ):
    def decorator(func):
        func.params = {
            "summary": summary,
            "description": decription,
            "response_description": response,

        }
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Appeler la fonction originale et obtenir son résultat
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
            # Appeler la fonction originale et obtenir son résultat
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorator


def Controller():
    pass

def Get():
    pass

def Post():
    pass

def Put():
    pass

def Delete():
    pass

