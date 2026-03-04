from fastapi.responses import HTMLResponse
from __nexy__.src.routes.index import Index
from __nexy__.src.routes.layout import Layout
from nexy.cli.commands.utilities.console import console
from nexy.decorators import UseResponse


def add():
    print("")


class useView :
    def __init__(self):
        pass
    def __new__(self, body,**arg):
        
        return HTMLResponse(body)
    
def GET(id:str= None)->HTMLResponse: 
    
    return useView(Layout(Index()))