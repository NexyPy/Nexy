from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from fastapi import APIRouter


@dataclass
class Node:
    pass


@dataclass
class ComponentNode(Node):
    name: str
    props: dict[str, str]
    children: list[Node] = field(default_factory=list)


@dataclass
class TextNode(Node):
    content: str


@dataclass
class NexyModule:
    name: str
    frontmatter: str
    template: list[Node]


@dataclass
class ScanResult:
    logic_block: str
    template_block: str

    @property
    def frontmatter(self) -> str:
        return self.logic_block

    @property
    def template(self) -> str:
        return self.template_block


@dataclass
class Binding:
    name: str
    value: Any
    is_prop: bool = False
    data_type: str = "any"


@dataclass
class NexyProp:
    name: str
    type: str
    default: str | None = None


class ComponentType(Enum):
    NEXY = "nexy"
    VUE = "vue"
    SVELTE = "svelte"
    REACT = "react"
    SOLID = "solid"
    PREACT = "preact"
    JSON = "json"
    MDX = "mdx"
    UNKNOWN = "unknown"


@dataclass
class NexyImport:
    path: str
    symbol: str | None = None
    alias: str | None = None
    raw_source: str = ""
    extension: str = ""
    comp_type: ComponentType = ComponentType.UNKNOWN


@dataclass
class LogicResult:
    nexy_imports: list[NexyImport] = field(default_factory=list)
    props: list[NexyProp] = field(default_factory=list)
    python_code: str = ""
    css_imports: list[str] = field(default_factory=list)


@dataclass
class ComponentUsage:
    name: str
    attributes: dict[str, str]
    is_self_closing: bool


@dataclass
class TemplateResult:
    converted_html: str
    used_components: set[str]


@dataclass
class ContextModel:
    key: str
    value: str


@dataclass
class ParserModel:
    frontmatter: str
    template: str
    props: list[NexyProp]
    context: list[ContextModel] = field(default_factory=list)
    styles: list[str] = field(default_factory=list)


@dataclass
class FFModel:
    name: str
    render: str
    extension: list[str] = field(default_factory=list)


class NexyConfigModel:
    useAliases: dict[str, str] | None = None
    useRouter: APIRouter | None = None
    usePort: int = 3000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy"
    useDocsUrl: str = "/docs"
    useRedocsUrl: str | None = "/redocs"
    useDocs: bool = True
    useVite: bool = False
    useViteDevUrl: str | None = None
    useFF: list[FFModel] = []
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = []
    useMiddlewares: list[Any] = []
    useCORS: dict | None = None
    useGZip: dict | None = None
    useTrustedHost: dict | None = None
    useHTTPSRedirect: bool = False
    useSession: dict | None = None
    useAuth: dict | None = None
    useSslKeyfile: str | None = None
    useSslCertfile: str | None = None
