from nexy.decorators import Controller
from nexy.decorators import UseRoute

@Controller("/blog/{version}", tags=["Blog"])
class BlogController:
    def __init__(self):
        self.posts = [
            {"id": 1, "title": "First Post", "content": "This is the first post."},
            {"id": 2, "title": "Second Post", "content": "This is the second post."},
        ]
    def GET(self, version: int):
        print(f"Blog version: {version}")
        # 2/0
        return {"version": version, "posts": self.posts}
    def post(self, version: int, post: dict):
        print(f"Blog version: {version}")
        new_post = {"id": len(self.posts) + 1, **post}
        self.posts.append(new_post)
        return new_post
   