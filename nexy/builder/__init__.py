from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config

class Builder:
    def __init__(self):
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()

    def build(self) -> None:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        for file in files:
            input_path = file.as_posix()
            self.compiler.compile(input=input_path)

# if __name__ == "__main__":
#     builder = Builder()
#     builder.build()

__all__ = ["Builder"]
