from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List, Dict, Optional


@dataclass
class Node:
    pass


@dataclass
class ComponentNode(Node):
    name: str
    props: Dict[str, str]
    children: List[Node] = field(default_factory=list)


@dataclass
class TextNode(Node):
    content: str


@dataclass
class NexyModule:
    name: str
    frontmatter: str
    template: List[Node]


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
    default: Optional[str] = None


class ComponentType(Enum):
    NEXY = "nexy"
    VUE = "vue"
    SVELTE = "svelte"
    REACT = "react"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class NexyImport:
    path: str
    symbol: Optional[str] = None
    alias: Optional[str] = None
    raw_source: str = ""
    extension: str = ""
    comp_type: ComponentType = ComponentType.UNKNOWN


@dataclass
class LogicResult:
    nexy_imports: List[NexyImport] = field(default_factory=list)
    props: List[NexyProp] = field(default_factory=list)
    python_code: str = ""


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
class PaserModel:
    frontmatter: str
    template: str
    props: list[NexyProp]
    context: list[ContextModel] = field(default_factory=list)


class NexyConfigModel:
    useAliases: dict[str, str] | None = None
    useRouter: Any | None = None
    usePort: int = 8000
    useHost: str = "0.0.0.0"
    useTitle: str = "Nexy"
    useDocsUrl: str = "/docs"
    useDocs: bool = True
    useVite: bool = False
    useFF: list[str] = field(default_factory=list)
    useMarkdownExtensions: list[str] = []
    excludeDirs: list[str] = []
    

