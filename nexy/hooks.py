from pathlib import Path
import re
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from markupsafe import Markup

def find_layouts(path):
    """
    Finds layout.html files by traversing up from specified path to 'app'
    Returns layouts in nesting order (app -> deeper)
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

    # Reverse layouts to apply from root to leaf
    layouts.reverse()
    return layouts

import re

def replace_block_component(match):
    component_name = match.group(1)
    children = match.group(3) or ""
    attrs_str = match.group(2) or ""
    attrs = {}

    # Extraction des attributs
    for attr in re.finditer(r'(\w+)=["\']?([^"\'>]+)["\']?', attrs_str):
        attr_name = attr.group(1)
        attr_value = attr.group(2)
        if attr_value.startswith("{{") and attr_value.endswith("}}"):
            attr_value = attr_value[2:-2].strip()  # Keep as is, don't quote
            attrs[attr_name] = attr_value
        else:
            attrs[attr_name] = f'"{attr_value}"' # Quote regular string attributes

    # Récursion sur les enfants pour transformer les composants imbriqués
    children = re.sub(r'<([A-Za-z]+)( [^>]*)?>(.*?)</\1>', replace_block_component, children, flags=re.DOTALL)

    if component_name[0].isupper():
        

        attrs_str = ", ".join(f"{name}={value}" for name, value in attrs.items())  # Convert attrs to string

        #  Handle cases with no attributes more gracefully
        if attrs_str:
            component_name = f"@call {component_name}({attrs_str})!\n{children}\n@endcall!"
        else:  # No attributes, simpler call
            component_name = f"@call {component_name}!\n{children}\n@endcall!"

        return component_name

    return match.group(0)



# Exemple de fonction pour les balises auto-fermantes
def replace_self_closing(match):
    component_name = match.group(1)
    attrs_str = match.group(2) or ""
    attrs = {}

    # Extraction des attributs
    for attr in re.finditer(r'(\w+)=["\']?([^"\'>]+)["\']?', attrs_str):
        attr_name = attr.group(1)
        attr_value = attr.group(2)
        if attr_value.startswith("{{") and attr_value.endswith("}}"):
            attr_value = attr_value[2:-2].strip()
            attrs[attr_name] = attr_value
        else:
            attrs[attr_name] = f'"{attr_value}"'

    if component_name[0].isupper():
        attrs_str = ", ".join(f"{name}={value}" for name, value in attrs.items())
        return "{{ " + component_name + "(" + attrs_str + ") }}" 

    return match.group(0)


def componentsParser(template):
    # Vérification s'il y a des balises avec majuscule
    if re.search(r'<[A-Z][a-zA-Z]*', template):
        # Ordre important : block components avant self-closing
        template = re.sub(r'<([A-Za-z]+)( [^>]*)?>(.*?)</\1>', replace_block_component, template, flags=re.DOTALL)
        template = re.sub(r'<([A-Za-z]+)( [^>]*)?/>', replace_self_closing, template)
    return Markup(template)

env = Environment(
    loader=FileSystemLoader("."),
    auto_reload=True,
    # autoescape=True,
    block_start_string="@!",
    block_end_string="!",
    trim_blocks= True,
    lstrip_blocks= True,
    comment_start_string="<!--",
    comment_end_string="-->",
)

def useView(data, path):
    """
    Renders a view with its hierarchically nested layouts
    :param data: Data to pass to templates
    :param path: View path (relative to app folder)
    """
    try:
        layouts = find_layouts(f"{path}/")
        # Load view
        with open(f"{path}/view.html", "r") as f:
            view_content = f.read()
        preprocessed_view_content = componentsParser(view_content)
        view_template = env.from_string(preprocessed_view_content) 
        
        content = view_template.render(**data)
        
        # Apply layouts from root to leaf, nesting content
        for layout_path in layouts:
            layout_template = env.get_template(layout_path)
            content = layout_template.render(children=content, **data)
        
        return HTMLResponse(content=content)
    
    except TemplateNotFound as e:
        try:
            error_template = env.get_template(f"{path}/404.html")
            return HTMLResponse(content=error_template.render(error=str(e)), status_code=404)
        except TemplateNotFound:
            return HTMLResponse(content=f"Template not found: {str(e)}", status_code=404)

    except Exception as e:
        try:
            error_template = env.get_template("errors/500.html")
            return HTMLResponse(
                content=error_template.render(error=str(e)), 
                status_code=500
            )
        except TemplateNotFound:
            return HTMLResponse(content=f"Error: {str(e)}", status_code=500)

def useActionView(data, path):
    """
    Renders view for action responses
    """
    try:
        view_template = env.get_template(f"{path}/view.html")
        view_template = componentsParser(view_template)
        content = view_template.render(**data)
        return HTMLResponse(content=content)
    except TemplateNotFound:
        return data

class State:
    def __init__(self, initial_value):
        self.value = initial_value
        
    def get(self):
        return self.value
    
    def set(self, new_value):
        self.value = new_value
        return self.value

class Fetch:
    def __init__(self):
        pass