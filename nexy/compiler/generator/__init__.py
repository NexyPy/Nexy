
import os
from nexy.core.models import PaserModel
from .logic import LogicGenerator
from .template import TemplateGenerator


class Generator:
    def __init__(self) -> None:
        self.output : str
        self.source : PaserModel
        self.template = TemplateGenerator()
        self.logic = LogicGenerator()

    def generate(self, output: str, source: PaserModel) -> bool:
        self.source = source
        try:
            directory = os.path.dirname(output)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            self.logic.generate(
                template_path=output,
                source=self.source
                )
            self.template.generate(output=output,source=self.source.template)
        except Exception as e:
            print(f"Error writing to file '{output}': {e}") 
            return False
    


__all__ = ["Generator"]