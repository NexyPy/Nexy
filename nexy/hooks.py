from fastapi.responses import  HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def useView(data,path):
    
    env = Environment(loader=FileSystemLoader("views"))   
    
    try:
        
        template = env.get_template(path)
        return template.render(data)
    
    except TemplateNotFound:
        return HTMLResponse(content=f"Template non trouvé : {path}", status_code=404)
    except Exception as e:
        return HTMLResponse(content=f"Erreur lors du rendu du template : {str(e)}", status_code=500)

