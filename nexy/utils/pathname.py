class PathName :
    def __init__(self, name) :
        self.name = name

    def __str__(self) :
        return self.name
    
    def normalize(self) :
        return self.name.replace(" ", "_").lower()
    
    