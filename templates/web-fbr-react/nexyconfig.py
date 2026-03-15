from nexy.core.models import NexyConfigModel
from nexy.frontend import react

class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + React)"
    useVite = True
