from nexy.core.models import NexyConfigModel
from nexy.frontend import vue

class NexyConfig(NexyConfigModel):
    useFF = [vue()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + Vue)"
    useVite = True
