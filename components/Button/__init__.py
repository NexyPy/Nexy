from nexy.decorators import action, component, use
from typing import Any

@action()
async def delete():
    return "delete"

@component(
    imports=[delete]
)
def Card(caller: Any):
    children = caller()
    return { "children": children }

@component(
    imports=[delete,Card]
)
def Button(text: str, type: str = "primary", action: str = None):
    
    return {"text": text, "type": type, "action": action, "name": "Button"}