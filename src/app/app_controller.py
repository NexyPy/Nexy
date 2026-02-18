from .app_services import UserService
from nexy.decorators import Controller

@Controller()
class UserController:
    # Injection automatique basée uniquement sur le type 'UserService'
    # Le nom du paramètre 'service' n'a pas d'importance
    def __init__(self, service: UserService):
        self.service = service

    def get(self):
        return self.service.get_users()

