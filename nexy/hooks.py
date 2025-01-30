from pathlib import Path
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import os

def find_layouts(path):
    """
    Trouve les fichiers layout.html en remontant depuis le chemin spécifié jusqu'à 'app'
    Retourne les layouts dans l'ordre d'imbrication (app -> plus profond)
    """
    layouts = []
    path_obj = Path(path)

    while path_obj.parts:
        current_path = Path(*path_obj.parts)
        layout_file = current_path / "layout.html"

        if layout_file.exists():
            layouts.append(str(layout_file).replace("\\","/"))

        if path_obj.parts[-1] == "app":
            break

        path_obj = path_obj.parent

    return layouts

env = Environment(
            loader=FileSystemLoader("."),
            auto_reload=True
        )
def useView(data, path):
    """
    Rendu d'une vue avec ses layouts imbriqués hiérarchiquement
    :param data: Données à passer aux templates
    :param path: Chemin de la vue (relatif au dossier app)
    """
    try:
        
        
        
        layouts = find_layouts(f"{path}/")
        # Charger la vue
        view_template = env.get_template(f"{path}/view.html")
        content = view_template.render(**data)
        # Appliquer les layouts successivement
        for layout_path in layouts:
            print(layout_path)
            layout_template = env.get_template(layout_path)
            content = layout_template.render(children=content, **data)
        
        return HTMLResponse(content=content)
    
    except TemplateNotFound as e:
        try:
            error_template = env.get_template(f"{path}/404.html")
            return HTMLResponse(content=error_template.render(error=str(e)), status_code=404)
        except TemplateNotFound:
            return HTMLResponse(content=f"Template hgh non trouvé : {str(e)}", status_code=404)

    except Exception as e:
        try:
            error_template = env.get_template("errors/500.html")
            return HTMLResponse(
            content=error_template.render(error=str(e)), 
            status_code=500
        )
        except TemplateNotFound:
            return HTMLResponse(content=f"Template non trouvé : {str(e)}", status_code=500)

       
        
