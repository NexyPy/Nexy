from .app_controller import UserController
from nexy import Module
from src.app.blog.blog_module import BlogModule


@Module(
    controllers=[UserController],
    providers=[] ,
    imports=[BlogModule],
)
class AppModule:
    pass


