from fastapi.responses import HTMLResponse
from nexy.decorators import HTTPResponse


@HTTPResponse(type=HTMLResponse)
def GET(id:int):
    print("yes")
    return {"id":id}