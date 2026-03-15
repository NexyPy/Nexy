from nexy.core.models import NexyConfigModel
from nexy.frontend import preact

class NexyConfig(NexyConfigModel):
    useFF = [preact()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + Preact)"
    useVite = True
