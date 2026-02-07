from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler

class Builder:
    def __init__(self):
        self.discovery = Discovery()
        self.compiler = Compiler()

    def build(self) -> None:
        files = self.discovery.scan(".")
        for file in files:
            input_path = file.as_posix()
            self.compiler.compile(input=input_path)

if __name__ == "__main__":
    builder = Builder()
    builder.build()

__all__ = ["Builder"]
