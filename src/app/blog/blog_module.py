from nexy.decorators import Module
from src.app.blog.blog_controller import BlogController


@Module(prefix="/blog")
class BlogModule:
    controllers = [BlogController]
    
