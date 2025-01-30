from fastapi.responses import HTMLResponse
from nexy.decorators import CustomResponse


@CustomResponse(type=HTMLResponse)
def GET(id:int):
    print("yes")
    return {"id":id}