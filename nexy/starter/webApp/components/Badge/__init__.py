from nexy import  Component

@Component()
def Badge(caller):
    return {"children":caller()}