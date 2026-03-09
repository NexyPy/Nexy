from nexy.core.models import NexyConfigModel

class NexyConfig(NexyConfigModel):
    useFF = ["fbr"]
    useTitle: str = "Nexy API (FBR)"
