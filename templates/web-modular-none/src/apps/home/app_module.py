from nexy.decorators import Module
from .app_controller import AppController

@Module()
class AppModule:
    controllers = [AppController]
    providers = []
    imports = []
