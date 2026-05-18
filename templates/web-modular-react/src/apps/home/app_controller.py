from nexy.decorators import Controller
from nexy.hooks import useViews

@Controller()
class AppController:
    def __init__(self):
        """Initializes the AppController."""
        pass
    async def get(self):
        """Renders the main page using a layout and home view."""
        return useViews('src/apps/home/app_view.nexy')

