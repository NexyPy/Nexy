from typing import Any
from actions import count, go, reset
from components.Button import Button,Card
from nexy import HTTPResponse, HTMLResponse
from nexy.decorators import Action, Component,  use

@Component(
    imports=[Button, Card]
)
def View():
    
    return {"users":"<h1>Hello</h1>","id":23}

users = [{"id":1, "name":"Espoir"}]

@Component(
    imports=[Button, Card]
)
def Layout(children):

    menus = [{"href":"/","name":"Home"}, {"href":"/eco","name":"Eco"}, {"href":"/eco/113","name":"Eco 1"}]
    return {"children":children,"menus":menus}
# @HTTPResponse(type=HTMLResponse)
# def GET():

#    return  View()


    

@HTTPResponse(type=HTMLResponse)
async def POST(delete = None, add= None, id=None,name=None):
  
    if delete and len(users)>=1 :
        users.pop(len(users)-1)
    elif add:
        user = {"id":len(users)+1, "name":f"user {len(users)+1}"}
        users.append(user)
    else:
        pass
    return {"users":users,"count":count.value , "add":go.action_path,"reset":reset.action_path}


@Action()
async def add():
    return "salue"



@Action()
async def delete():
    return {"message":"Espoir serait beau", "action":use(add)}

@Action(["id"])
async def delete(id:Any):
    return id



