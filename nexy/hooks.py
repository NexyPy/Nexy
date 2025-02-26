"""
Author: Espoir Loém

This module provides hooks and utilities for rendering views and components in the Nexy application.
"""

from pathlib import Path
import re
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from markupsafe import Markup
from jinja2.ext import Extension

from nexy.utils import importModule


def find_controllers(path):
    """
    Finds controller.py files by traversing up from the specified path to 'app'.
    Returns controllers in nesting order (app -> deeper).
    """
    controllers = []
    path_obj = Path(path)

    while path_obj.parts:
        current_path = Path(*path_obj.parts)
        controller_file = current_path / "controller.py"

        if controller_file.exists():
            controllers.append(str(controller_file).replace("\\", "."))

        if path_obj.parts[-1] == "app":
            break

        path_obj = path_obj.parent

    return controllers[::-1]  # Reverse controllers to apply from root to leaf


env = Environment(
    loader=FileSystemLoader("."),
    auto_reload=True,
    block_start_string="{!",
    block_end_string="}",
    trim_blocks=True,
    lstrip_blocks=True,
    comment_start_string="<!--",
    comment_end_string="-->",
)

def useView(code, path, **data):
    """
    Renders a view with its hierarchically nested layouts.
    :param data: Data to pass to templates
    :param path: View path (relative to app folder)
    """
    try:
        controllers = find_controllers(path)
        content = code
        print("controllers",controllers)
        for controller_path in reversed(controllers):
            controller_path = controller_path.replace(".py", "")
            controller_module = importModule(controller_path)
            if hasattr(controller_module, 'Layout'):
                content = controller_module.Layout(children=content, **data)
        return HTMLResponse(content=content)
    
    except TemplateNotFound as e:
        return handle_template_not_found(path, e)

    except Exception as e:
        return handle_generic_error(e)

def handle_template_not_found(path, error):
    """
    Handles the TemplateNotFound exception by attempting to render a 404 error page.
    """
    try:
        error_template = importModule(f"{path}.controller")
        if hasattr(error_template, 'Error'):
            content = error_template.Error(error=str(error))
        return HTMLResponse(content=content, status_code=404)
    except TemplateNotFound:
        return HTMLResponse(content=f"Template not found: {str(error)}", status_code=404)

def handle_generic_error(error):
    """
    Handles generic exceptions by attempting to render a 500 error page.
    """
    try:
        error_template = env.get_template("errors/500.html")
        return HTMLResponse(
            content=error_template.render(error=str(error)), 
            status_code=500
        )
    except TemplateNotFound:
        return HTMLResponse(content=f"Error: {str(error)}", status_code=500)

class State:
    """
    A simple state management class.
    """
    def __init__(self, initial_value):
        self.value = initial_value
        
    def get(self):
        return self.value
    
    def set(self, new_value):
        self.value = new_value
        return self.value
