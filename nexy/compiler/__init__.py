from nexy.compiler.parser import Parser
from nexy.compiler.generator import Generator
from nexy.core.models import PaserModel
from nexy.nexyconfig import NexyConfig
    

def is_nexy_file(file_path: str) -> bool:
    return file_path.endswith(".nexy")

def is_mdx_file(file_path: str) -> bool:
    return file_path.endswith(".mdx")

class Compiler:
    def __init__(self) -> None:
        self.input:str =""
        self.output :str | None = None
        self.parser = Parser()
        self.generator = Generator()
        self.source_code :str = ""
        self.config = NexyConfig()

    def _load_source(self) -> str:
        try:
            with open(self.input, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File '{self.input}' not found.") from e
    def compile(self, input: str,output: str | None = None) -> None:
        self.input = input
        self.output = output
        self.source_code = self._load_source()
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

# input = "src/routes/about.mdx"
# ouput = "__nexy__/src/routes/index"

# code = Compiler()
# code.compile(input=input)
__all__ = ["Compiler"]