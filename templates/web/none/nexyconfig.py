from nexy.core.models import NexyConfigModel


class NexyConfig(NexyConfigModel):
    useFF = [ ]
    useAliases: dict[str, str] = {"@": "src/components"}
    useTitle: str = "Nexy gh"
