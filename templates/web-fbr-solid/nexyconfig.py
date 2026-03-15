from nexy.core.models import NexyConfigModel
from nexy.frontend import solid

class NexyConfig(NexyConfigModel):
    useFF = [solid()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + Solid)"
    useVite = True
