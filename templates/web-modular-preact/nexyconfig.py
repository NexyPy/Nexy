from nexy.core.models import NexyConfigModel
from nexy.frontend import preact
from src.apps.home.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = [preact()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (Modular + Preact)"
    useVite = True
    useRouter = AppModule
