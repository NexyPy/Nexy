from nexy.core.models import NexyConfigModel
from src.apps.home.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useTitle: str = "Nexy Web (Modular)"
    useVite: bool = True
    useAliases = {"@": "src"}
    useRouter = AppModule
