from nexy import HTTPResponse, HTMLResponse



users = ["user 1"]
@HTTPResponse(type=HTMLResponse)
def GET():
    return {"users":users}

@HTTPResponse(type=HTMLResponse)
def POST(delete = None, add= None):
    if delete and len(users)>=1 :
        users.pop(len(users)-1)
    elif add:
        users.append(f"useer {len(users)+1}")
    else:
        pass
    return {"users":users}

