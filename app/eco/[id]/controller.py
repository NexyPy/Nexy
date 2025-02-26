from nexy.decorators import Component


@Component()
def View(id:int):
    return {"users":"<h1>Hello</h1>","id":id}

@Component()
def Layout(children):
    return {"children":children}

