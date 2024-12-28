
from fastapi.responses import  HTMLResponse
def useView(content):
    return HTMLResponse(content=f"{content}")

