from nexy.core.models import NexyConfigModel

class NexyConfig(NexyConfigModel):
    useTitle: str = "Nexy Web (FBR)"
    useVite: bool = True
    useAliases = {"@": "src"}
