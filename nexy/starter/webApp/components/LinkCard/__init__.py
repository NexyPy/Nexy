from nexy import Component
@Component()
def LinkCard(title:str, description:str,href:str):
    return {"title":title,"description":description,"href":href}