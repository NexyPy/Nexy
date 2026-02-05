from nexy.core.models import PaserModel
from nexy.nexyconfig import NexyConfig
from parser import Parser
from generator import Generator

def is_nexy_file(file_path: str) -> bool:
    return file_path.endswith(".nexy")

def is_mdx_file(file_path: str) -> bool:
    return file_path.endswith(".mdx")

class Compiler:
    def __init__(self, input: str,output: str | None = None) -> None:
        self.input = input
        self.output = output
        self.parser = Parser()
        self.generator = Generator()
        self.source_code :str = self._load_source()
        self.config = NexyConfig()

    def _load_source(self) -> str:
        try:
            with open(self.input, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File '{self.input}' not found.")
    def compile(self) -> None:
        
        if  is_nexy_file(self.input):
            if self.output is None:
                self.output = self.config.NAMESPACE + "/"+ self.input.replace(".nexy", ".html")
        elif is_mdx_file(self.input):
            if self.output is None:
                self.output = self.config.NAMESPACE +"/"+ self.input.replace(".mdx", ".md")
        
        else:
            print(f"Error: File '{self.input}' is not a nexy or mdx component")
            return None
        
        CODE_PARSED:PaserModel = self.parser.process(source_code=self.source_code, current_file=self.input)
        self.generator.generate(self.output, CODE_PARSED)
        


        # compiled_module = parser.parse()

input = "src/routes/about.mdx"
ouput = "__nexy__/src/routes/index"

code = Compiler(input=input)
code.compile()
__all__ = ["Compiler"]