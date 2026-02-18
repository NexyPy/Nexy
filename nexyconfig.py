from nexy.core.models import NexyConfigModel
from nexy.router import FileBasedRouter


class NexyConfig(NexyConfigModel):
    useAliases: dict[str, str] = {"@": "src/components"}
    useRouter = FileBasedRouter
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy"
    useDocsUrl: str = "/docs"
    useDocs: bool = True
    useVite: bool = False
    useMarkdownExtensions: list[str] = []
