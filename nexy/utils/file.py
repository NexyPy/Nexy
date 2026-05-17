
from pathlib import Path


class File :
    def __init__ (self, path) :
        self.path = path
    def read (self) :
        with open(self.path, "r", encoding="utf-8") as f :
            return f.read()
    def write (self, content) :
        with open(self.path, "w", encoding="utf-8") as f :
            f.write(content)
    def exists (self) :
        return Path(self.path).exists()
    
    def delete (self) :
        if self.exists() :
            Path(self.path).unlink()
        else :
            print(f"File {self.path} not exists")
            return False
        return True
    def create (self) :
        if not self.exists() :
            Path(self.path).touch()
        else :
            print(f"File {self.path} already exists")
            return False
        return True
    