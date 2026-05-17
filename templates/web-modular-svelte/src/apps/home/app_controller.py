from nexy.decorators import Controller
from nexy.hooks import useViews

@Controller()
class AppController:
    async def get(self):
        """Renders the main page using a layout and home view."""
        return useViews("src/apps/home/layout.nexy", context={
            "children": useViews("src/apps/home/home_view.nexy")
        })
