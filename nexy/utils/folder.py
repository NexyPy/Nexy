from pathlib import Path

from nexy.utils.pathname import PathName


class Folder :
    def __init__ (self, path) :
        self.path = path
    def exists (self) :
        return Path(self.path).exists()
    def create (self) :
        if not self.exists() :
            Path(self.path).mkdir(parents=True, exist_ok=True)
        else :
            print(f"Folder {self.path} already exists")
            return False
        return True
    def delete (self) :
        if self.exists() :
            Path(self.path).rmdir()
        else :
            print(f"Folder {self.path} not exists")
            return False
        return True
    
    def normalize (self) :
        return PathName(self.path).normalize()
