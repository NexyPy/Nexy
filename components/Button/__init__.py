from nexy.decorators import Action, Component, use
from typing import Any

@Action()
async def delete():
    return "delete"

@Component(
    imports=[delete]
)
def Card(caller: Any):
    children = caller()
    return { "children": children }

@Component(
    imports=[delete,Card]
)
def Button(text: str, type: str = "primary", action: str = None):
    
    return {"text": text, "type": type, "action": action, "name": "Button"}