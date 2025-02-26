"""
Author: Espoir Loém

This module provides utility functions for the Nexy application, including
string manipulation, dynamic route conversion, module importation, and
template component parsing.
"""

import re
import importlib
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
