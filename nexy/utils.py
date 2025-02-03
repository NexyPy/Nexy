import re
import importlib

from fastapi import Path
from markupsafe import Markup
# 
def deleteFistDotte(string:str)-> str:
    if string.startswith('.'):
        return re.sub(r'^.', '', string)
    else:
        return string
    
def dynamicRoute(route_in:str)-> str:

    # Remplacer [id] par {id}
    route_out = re.sub(r"\[([^\]]+)\]", r"{\1}",route_in)
    # Remplacer {_slug} par {slug:path} pour capturer plusieurs segments
    route_out = re.sub(r"\{_([^\}]+)\}", r"{\1}:path", route_out)

    return route_out

def convertPathToModulePath(path:str)->str:
    return re.sub(r"\\|/", ".", path)

def importModule(path: str):
    try:
        module = importlib.import_module(path)
        return module
    except ModuleNotFoundError as e:
        print(f"Error importing module '{path}': {e}")
        raise




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
