from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
import questionary
from nexy.__version__ import __Version__
from nexy.utils.console import console
from nexy.i18n import t


class InitProject:
    def __init__(self) -> None:
        self.version = __Version__().get()
        self.config = {}

 
    def check_nexy(): pass

   
    def _is_empty_dir(self, path: Path) -> bool:
        return not any(path.iterdir())

    
    def _move_subdir_to_root(self, root: Path, subdir: Path) -> None:
        """Moves all contents from a subdirectory to the root and removes the subdirectory."""
        source = root / subdir
        if not source.exists():
            return
            
        for item in source.iterdir():
            target = root / item.name
            if target.exists():
                if target.is_dir():
                    shutil.rmtree(target, ignore_errors=True)
                else:
                    target.unlink()
            shutil.move(str(item), str(root))
            
        # Remove empty parent dirs of the subdir
        current = source
        while current != root:
            parent = current.parent
            shutil.rmtree(current, ignore_errors=True)
            current = parent
            if any(current.iterdir()):
                break

    def resolve_template_path(self) -> str:
        """Resolves the template folder path based on the user's choices."""
        router = "fbr" if self.config.get('FBRouter') else "modular"
        project_type = self.config.get('project_type', 'web')
        client_framework = self.config.get('client_framework', 'none').lower()
        
        # Structure: templates/[project_type]-[router]-[client_framework]
        if project_type == "api":
            return f"templates/api-{router}"
        
        return f"templates/{project_type}-{router}-{client_framework}"

    