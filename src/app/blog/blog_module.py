from nexy.decorators import Module
from src.app.blog.blog_controller import BlogController


@Module(
    controllers=[BlogController],
)
class BlogModule:
    pass
