from nexy import CustomResponse, HTMLResponse



users = ["user 1"]
@CustomResponse(type=HTMLResponse)
def GET():
    return {"users":users}

@CustomResponse(type=HTMLResponse)
def POST(delete = None, add= None):
    if delete and len(users)>=1 :
        users.pop(len(users)-1)
    elif add:
        users.append(f"useer {len(users)+1}")
    else:
        pass
    return {"users":users}

