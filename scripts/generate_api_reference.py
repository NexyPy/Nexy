import os
import inspect
import importlib
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.getcwd())

def generate_api_docs():
    output_dir = Path("_docs/en/06. Reference")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    modules_to_document = [
        ("nexy.app", "Nexy Application"),
        ("nexy.router", "Routing"),
        ("nexy.template", "Templates"),
        ("nexy.core.models", "Configuration Models"),
    ]
    
    for module_path, title in modules_to_document:
        try:
            module = importlib.import_module(module_path)
            content = f"# {title}\n\n"
            content += f"Reference for the `{module_path}` module.\n\n"
            
            # Document classes
            classes = inspect.getmembers(module, inspect.isclass)
            for name, cls in classes:
                if cls.__module__ == module_path and not name.startswith("_"):
                    content += f"## class `{name}`\n\n"
                    if cls.__doc__:
                        content += f"{cls.__doc__.strip()}\n\n"
                    
                    # Document methods
                    methods = inspect.getmembers(cls, inspect.isfunction)
                    for m_name, m_func in methods:
                        if not m_name.startswith("_"):
                            sig = inspect.signature(m_func)
                            content += f"### `{m_name}{sig}`\n\n"
                            if m_func.__doc__:
                                content += f"{m_func.__doc__.strip()}\n\n"
            
            # Document functions
            functions = inspect.getmembers(module, inspect.isfunction)
            for name, func in functions:
                if func.__module__ == module_path and not name.startswith("_"):
                    sig = inspect.signature(func)
                    content += f"## function `{name}{sig}`\n\n"
                    if func.__doc__:
                        content += f"{func.__doc__.strip()}\n\n"
            
            filename = f"03. {title.replace(' ', '')}.md"
            with open(output_dir / filename, "w", encoding="utf-8") as f:
                f.write(content)
                
        except Exception as e:
            print(f"Error documenting {module_path}: {e}")

if __name__ == "__main__":
    generate_api_docs()
