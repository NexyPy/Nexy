
import os
from nexy.core.models import PaserModel
from .logic import LogicGenerator
from .template import TemplateGenerator


class Generator:
    def __init__(self) -> None:
        self.output: str = ""
        self.source: PaserModel | None = None
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()

    def generate(self, output: str, source: PaserModel) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            if directory:
                os.makedirs(directory, exist_ok=True)
            self.logic.generate(template_path=output, source=self.source)
            self.template.generate(output=output, source=self.source.template)
            self._generate_init(directory)
            return True
        except Exception as e:
            print(f"Error writing to file '{output}': {e}")
            return False
    
    def _generate_init(self, directory: str) -> None:
        init_file = os.path.join(directory, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("")


__all__ = ["Generator"]