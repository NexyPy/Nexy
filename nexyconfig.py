from nexy.core.models import NexyConfigModel
from src.app.app_module import AppModule
from nexy.frontend import react


class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useAliases: dict[str, str] = {"@": "src/components"}
    useRouter =AppModule
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy gh"
    useDocs: bool = True
    useVite: bool = True
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = []
