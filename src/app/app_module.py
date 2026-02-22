from src.app.app_controller import UserController
from nexy.decorators import Module
from src.app.blog.blog_module import BlogModule


@Module()
class AppModule:
    controllers = [UserController]
    imports = [BlogModule]


