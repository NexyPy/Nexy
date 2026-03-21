from nexy.core.models import NexyConfigModel
from nexy.frontend import react

class NexyConfig(NexyConfigModel):
    useFF = [react()]
    # usePort = 4000
    useAliases = {"@": "src"}
    useTitle = "Nexy Web (FBR + React)"
    useVite = True
