from .app_controller import UserController
from nexy import Module


@Module(
    controllers=[UserController],
    providers=[] 
)
class AppModule:
    pass


