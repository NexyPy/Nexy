from nexy.builder.discovery import Discovery
from nexy.compiler import Compiler
from nexy.core.config import Config


class Builder:
    def __init__(self):
        self.discovery = Discovery()
        self.compiler = Compiler()
        self.config = Config()

        exclude_dirs = getattr(self.config, "excludeDirs", [])
        for name in exclude_dirs:
            self.discovery.add_excluded_dir(name)

    def build(self) -> None:
        files = self.discovery.scan(self.config.PROJECT_ROOT)
        for file in files:
            input_path = file.as_posix()
            self.compiler.compile(input=input_path)


__all__ = ["Builder"]
