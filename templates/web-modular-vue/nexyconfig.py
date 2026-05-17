from nexy.core.models import NexyConfigModel
from nexy.frontend import vue
from src.apps.home.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = [vue()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (Modular + Vue)"
    useVite = True
    useRouter = AppModule
