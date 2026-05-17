from nexy.decorators import Controller
from nexy.hooks import useViews

@Controller()
class AppController:
    async def GET(self):
        """Renders the main page using a layout and home view."""
        return useViews('src/apps/home/app_view.nexy')
