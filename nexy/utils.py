"""
Author: Espoir Loém

This module provides utility functions for the Nexy application, including
string manipulation, dynamic route conversion, module importation, and
template component parsing.
"""

import os
import re
import importlib
import sys
from typing import Any, Dict, List
from fastapi import Path
from markupsafe import Markup

def deleteFistDotte(string: str) -> str:
    """Removes the first dot from a string if it exists."""
    return string[1:] if string.startswith('.') else string

def dynamicRoute(route_in: str) -> str:
    """
    Converts dynamic route placeholders from square brackets to curly braces
    and handles slug paths.
    """
    route_out = re.sub(r"\[([^\]]+)\]", r"{\1}", route_in)
    return re.sub(r"\{_([^\}]+)\}", r"{\1}:path", route_out)

def convertPathToModulePath(path: str) -> str:
    """Converts a file path to a module path by replacing slashes with dots."""
    return path.replace("\\", ".").replace("/", ".")

def importModule(path: str):
    """Imports a module given its path and handles errors."""
    try:
        return importlib.import_module(path)
    except ModuleNotFoundError as e:
        print(f"Error importing module '{path}': {e}")
        raise

def find_layouts(path):
    """
    Finds layout.html files by traversing up from the specified path to 'app'.
    Returns layouts in nesting order (app -> deeper).
    """
    layouts = []
    path_obj = Path(path)

    while path_obj.parts:
        current_path = Path(*path_obj.parts)
        layout_file = current_path / "layout.html"

        if layout_file.exists():
            layouts.append(str(layout_file).replace("\\", "/"))

        if path_obj.parts[-1] == "app":
            break

        path_obj = path_obj.parent

    return layouts[::-1]  # Reverse layouts to apply from root to leaf

def replace_block_component(match):
    """
    Replaces block components in a template with a specific format.
    Handles attributes and nested components.
    """
    component_name = match.group(1)
    children = match.group(3) or ""
    attrs_str = match.group(2) or ""
    attrs = {
        attr.group(1): attr.group(2)[2:-2].strip() if attr.group(2).startswith("{{") and attr.group(2).endswith("}}") else f'"{attr.group(2)}"'
        for attr in re.finditer(r'(\w+)=["\']?([^"\'>]+)["\']?', attrs_str)
    }

    children = re.sub(r'<([A-Za-z]+)( [^>]*)?>(.*?)</\1>', replace_block_component, children, flags=re.DOTALL)

    if component_name[0].isupper():
        attrs_str = ", ".join(f"{name}={value}" for name, value in attrs.items())
        return f"@call {component_name}({attrs_str})!\n{children}\n@endcall!" if attrs_str else f"@call {component_name}!\n{children}\n@endcall!"

    return match.group(0)

def replace_self_closing(match):
    """
    Replaces self-closing components in a template with a specific format.
    Handles attributes.
    """
    component_name = match.group(1)
    attrs_str = match.group(2) or ""
    attrs = {
        attr.group(1): attr.group(2)[2:-2].strip() if attr.group(2).startswith("{{") and attr.group(2).endswith("}}") else f'"{attr.group(2)}"'
        for attr in re.finditer(r'(\w+)=["\']?([^"\'>]+)["\']?', attrs_str)
    }

    if component_name[0].isupper():
        attrs_str = ", ".join(f"{name}={value}" for name, value in attrs.items())
        return f"{{{{ {component_name}({attrs_str}) }}}}"

    return match.group(0)

def componentsParser(template):
    """
    Parses a template to replace custom components with a specific format.
    Handles both block and self-closing components.
    """
    if re.search(r'<[A-Z][a-zA-Z]*', template):
        template = re.sub(r'<([A-Za-z]+)( [^>]*)?>(.*?)</\1>', replace_block_component, template, flags=re.DOTALL)
        template = re.sub(r'<([A-Za-z]+)( [^>]*)?/>', replace_self_closing, template)
    return Markup(template)


cache_js_action = {}


def generate_js_action(func_name: str, path: str, url: str, params: List[str] = None, slug: List[str] =None) -> str:
    """
    Generates JavaScript function code for a Python action function and saves it to file.
    
    Args:
        func_name: Name of the function
        path: API endpoint path
        params: Optional list of parameter names
        slug: Optional list of slug segments
    
    Returns:
        JavaScript function code as string
    """
    params = params or []
    slug = slug or []
    params = [p for p in params if p not in slug]
    params_obj = ','.join(params)
    slug_obj = ','.join(f'{s}' for s in slug) if slug else ''
     
    # Generate async JS function with template literal
    args = ''
    if slug or params:
        slug_part = f"slugs = {{{slug_obj}}}, " if slug else ''
        # print(params_obj)
        params_part = f"queryParams={{{params_obj}}}" if params else ''
        args = f'{{{slug_part}{params_part}}}'.rstrip(', ')
    js_code = f"""
    
/**
 * Asynchronously calls the {func_name} function.
 * 
 * @param {{Object}} {args} - An object containing:
 *   {''.join([f"*   @param {{string}} {s} - Slug parameter.\n" for s in slug])}
 *   {''.join([f"*   @param {{string}} {p} - Query parameter.\n" for p in params])}
 * 
 * @returns {{Promise<Object>}} - The response data as a JSON object.
 * @throws Will throw an error if the HTTP request fails.
 */
export async function {func_name}({args}) {{
     if (typeof queryParams === 'object' ) {{
        queryParams = new URLSearchParams(queryParams);
     }}
    const url = `http://127.0.0.1:3000{url}{'' if len(params) == 0 else '?${queryParams?.toString()}'}`;
    
    try {{
        const response = await fetch(url, {{
            method: "POST",
            headers: {{"Content-Type": "application/json"}},
        }});
        
        if (!response.ok) throw new Error(`HTTP error! status: ${{response.status}}`);
        return await response.json();
    }} catch (error) {{
        console.error("Error calling {func_name}:", error);
        throw error;
    }}
}}"""

    # Minify the js_code
    import re
    js_code = re.sub(r'\s+', ' ', js_code).strip()
    # Handle file operations efficiently
    from pathlib import Path
    
    file_path = Path('./__pycache__/nexy').joinpath(path.lstrip('/'))
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    if path not in cache_js_action:
        cache_js_action[path] = js_code
    else:
        cache_js_action[path] += js_code

    file_path.write_text(cache_js_action[path])

    return js_code



# Analyze the file structure and extract route information
def find_routes(base_path: str) -> List[Dict[str, Any]]:
    routes = []
    
    # Verify if the 'app' folder exists
    if os.path.exists(base_path) and os.path.isdir(base_path):
        # Add app directory to Python path
        app_dir = os.path.abspath(base_path)
        if app_dir not in sys.path:
            sys.path.append(app_dir)
            
        # Explore the 'app' folder and its subfolders
        for root, dirs, files in os.walk(base_path):
            # Remove unwanted folders
            dirs[:] = [d for d in dirs if not d.startswith(("_", "node_module", "env", "venv", "nexy", ".", "public", "configs"))]

            route = {
                "pathname": f"{'/' if os.path.basename(root) == base_path else '/' + deleteFistDotte(os.path.relpath(root, base_path).replace('\\','/'))}",
                "dirName": root
            }
            controller = os.path.join(root, 'controller.py')
            middleware = os.path.join(root, 'middleware.py')
            service = os.path.join(root, 'service.py')
            actions = os.path.join(root, 'actions.py')

            # Check for files and add to dictionary
            if os.path.exists(controller):
                route["controller"] = convertPathToModulePath(f"{root}/controller")    
            if os.path.exists(middleware):
                route["middleware"] = convertPathToModulePath(f"{root}/middleware") 
            if os.path.exists(service):
                route["service"] = convertPathToModulePath(f"{root}/service") 
            if os.path.exists(actions):
                route["actions"] = convertPathToModulePath(f"{root}/actions")
            routes.append(route)

    return routes

