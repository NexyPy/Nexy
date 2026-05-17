
import os
from pathlib import Path
from nexy.core.models import PaserModel
from .logic import LogicGenerator
from .template import TemplateGenerator
from nexy.utils.console import console
from nexy.errors import NexyCompileError
from nexy.core.config import Config


class Generator:
    def __init__(self) -> None:
        self.output: str = ""
        self.source: PaserModel | None = None
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()

    def generate(self, output: str, source: PaserModel, source_path:str = None) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self.logic.generate(template_path=output, source=self.source, source_path=source_path)
            self.template.generate(output=output, source=self.source.template)
            self._generate_init(directory)
            return True
        except Exception as e:
            console.print(f"[red]nsc[/red] » Error writing to file '{output}': {e}")
            raise NexyCompileError(source_path=output, message=str(e))
    
    def _generate_init(self, directory: str) -> None:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")


__all__ = ["Generator"]
