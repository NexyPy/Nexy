from nexy.core.models import NexyConfigModel
from nexy.frontend import react
from nexy.router import FileBasedRouter
from src.app.app_module import AppModule


class NexyConfig(NexyConfigModel):
    useFF = [react()]
    useAliases: dict[str, str] = {"@": "src/components"}
    # useRouter = FileBasedRouter
    useRouter=AppModule
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy"
    useDocsUrl: str = "/docs"
    useDocs: bool = True
    useVite: bool = False
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = []
