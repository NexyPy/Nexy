from nexy.utils.fs.vfs import VFS


class TemplateGenerator:
    def __init__(self) -> None:
        self.vfs = VFS()

    def generate(self, output: str, source: str) -> None:
        self.vfs.write(output, source)
