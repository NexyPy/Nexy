from nexy.decorators import Component


@Component(

)
def View():
    return {"users":"<h1>Hello</h1>","id":23}

@Component()
def Layout(children):
    return {"children":children}

