from nexy.core.models import ParserModel


class TemplateGenerator:
    def __init__(self) -> None:
        pass

    def generate(self, output: str, source: str) -> None:
        with open(output, "w", encoding="utf-8") as f:
            f.write(source)