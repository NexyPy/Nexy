from nexy.core.models import NexyConfigModel
from nexy.frontend import react
from src.apps.home.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useAliases = {"@": "src/"}
    useTitle = "Nexy Web (Modular + React)"
    useVite = True
    useRouter = AppModule
    useDocs = True

