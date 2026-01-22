class Config:
    def __init__(self):
        self.options = {}
class NexyConfig(Config):
    def __init__(self):
        super().__init__()
        self.settings = {}