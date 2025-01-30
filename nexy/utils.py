import os
import re
import importlib

from fastapi import Path
# 
def deleteFistDotte(string:str)-> str:
    if string.startswith('.'):
        return re.sub(r'^.', '', string)
    else:
        return string
    
def dynamicRoute(route_in:str)-> str:

    # Remplacer [id] par {id}
    route_out = re.sub(r"\[([^\]]+)\]", r"{\1}",route_in)
    # Remplacer {_slug} par {slug:path} pour capturer plusieurs segments
    route_out = re.sub(r"\{_([^\}]+)\}", r"{\1}:path", route_out)

    return route_out

def convertPathToModulePath(path:str)->str:
    return re.sub(r"\\|/", ".", path)

def importModule(path: str):
    try:
        module = importlib.import_module(path)
        return module
    except ModuleNotFoundError as e:
        print(f"Error importing module '{path}': {e}")
        raise
