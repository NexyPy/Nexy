from nexy.decorators import Module
from .app_controller import AppController

@Module(
    controllers=[AppController],
    providers=[],
    imports=[],
)
class AppModule:
    pass
