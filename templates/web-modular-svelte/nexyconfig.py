from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte
from src.apps.app_module import AppModule

class NexyConfig(NexyConfigModel):
    useFF = [svelte()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (Modular + Svelte)"
    useVite = True
    useRouter = AppModule
