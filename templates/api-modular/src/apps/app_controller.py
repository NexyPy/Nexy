from nexy.decorators import Controller
from nexy.core.types import JsonResponse

@Controller()
class AppController:
    async def get(self) -> JsonResponse:
        return {"message": "Welcome to Nexy Modular API"}
