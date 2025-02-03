import app.actions 
from actions import count
from nexy import CustomResponse, HTMLResponse



users = [{"id":1, "name":"Espoir"}]
@CustomResponse(type=HTMLResponse)
def GET(delete = None, add= None, id=None):
    if delete and len(users)>=1 :
        users.pop(len(users)-1)
    elif add:
        user = {"id":len(users)+1, "name":f"user {len(users)+1}"}
        users.append(user)
    else:
        pass
    return {"users":users,"count":count.value}

def go():
    return "hdgg"

class PPP:
    def go():
        pass
    

@CustomResponse(type=HTMLResponse)
def POST(delete = None, add= None, id=None):
  

    if delete and len(users)>=1 :
        users.pop(len(users)-1)
    elif add:
        user = {"id":len(users)+1, "name":f"user {len(users)+1}"}
        users.append(user)
    else:
        pass
    return {"users":users,"count":count.value}


class Actions:
    def delete():
        pass

