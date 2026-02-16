from dataclasses import dataclass
from typing import Optional, Union

from fastapi import APIRouter


route = APIRouter()
@route.get("/config")
def get_config():   
    return'NexyConfig'

@route.get("/")
def get_root():
    return "Hello, Nexy!"

@route.get("/test")
def get_test():
    return "This is a test route."

@route.get("/users/{user_id}")
def get_user(user_id: bool):
    return {"user_id": user_id, "name": f"User {user_id}"}

class NexyConfig():
    ALIASES: dict[str, str] = {"@": "src/components"}
    ROOT_MODULE = route
    FILE_BASED_ROUTING: bool = True
