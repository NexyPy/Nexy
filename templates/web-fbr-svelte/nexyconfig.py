from nexy.core.models import NexyConfigModel
from nexy.frontend import svelte

class NexyConfig(NexyConfigModel):
    useFF = [svelte()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + Svelte)"
    useVite = True
