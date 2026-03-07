from nexy.compiler.parser import Parser
from nexy.compiler.generator import Generator
from nexy.core.models import PaserModel
from nexy.core.config import Config
from nexy.errors import NexyCompileError
from nexy.utils.console import console

def is_nexy_file(file_path: str) -> bool:
    return file_path.endswith(".nexy")

def is_mdx_file(file_path: str) -> bool:
    return file_path.endswith(".mdx")

class Compiler:
    def __init__(self) -> None:
        self.input: str = ""
        self.output: str | None = None
        self.parser = Parser()
        self.generator = Generator()
        self.source_code: str = ""
        self.config = Config()

    def _load_source(self) -> str:
        try:
            with open(self.input, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File '{self.input}' not found.") from e
    def compile(self, input: str, output: str | None = None) -> None:
        self.input = input
        self.output = output
        self.source_code = self._load_source()
        if is_nexy_file(self.input):
            if self.output is None:
                from nexy.core.string import StringTransform
                mapped = StringTransform.normalize_route_path_for_namespace(self.input)
                self.output = self.config.NAMESPACE + "/" + mapped.replace(".nexy", ".html")
        elif is_mdx_file(self.input):
            if self.output is None:
                from nexy.core.string import StringTransform
                mapped = StringTransform.normalize_route_path_for_namespace(self.input)
                self.output = self.config.NAMESPACE + "/" + mapped.replace(".mdx", ".md")
        
        else:
            msg = f"File '{self.input}' is not a nexy or mdx component"
            console.print(f"[red]nsc[/red] » {msg}")
            raise NexyCompileError(source_path=self.input, message=msg)
        
        try:
            CODE_PARSED: PaserModel = self.parser.process(source_code=self.source_code, current_file=self.input)
            self.generator.generate(self.output, CODE_PARSED)
        except NexyCompileError:
            raise
        except Exception as e:
            line = getattr(e, "lineno", None) or getattr(e, "line", None)
            col = getattr(e, "offset", None) or getattr(e, "column", None)
            msg = str(e)
            raise NexyCompileError(source_path=self.input, message=msg, line=line, column=col) from e
        


        # compiled_module = parser.parse()

# input = "src/routes/about.mdx"
# ouput = "__nexy__/src/routes/index"

# code = Compiler()
# code.compile(input=input)
__all__ = ["Compiler"]
