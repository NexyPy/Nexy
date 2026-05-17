from nexy.core.models import NexyConfigModel
from nexy.frontend import solid
from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = [solid()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (Modular + Solid)"
    useVite = True
    useRouter = AppModule
