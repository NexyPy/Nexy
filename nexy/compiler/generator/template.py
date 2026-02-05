from nexy.core.models import PaserModel


class TemplateGenerator:
    def __init__(self) -> None:
        pass

    def generate(self, output: str, source: str) -> None:
        with open(output, "w", encoding="utf-8") as file:
            file.write(source)
            return True