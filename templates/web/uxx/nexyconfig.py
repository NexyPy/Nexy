from nexy.core.models import NexyConfigModel

class NexyConfig(NexyConfigModel):
    useFF = ["fbr"]
    useAliases: dict[str, str] = {"@": "src/components"}
    useTitle: str = "Nexy Web (FBR + React)"
