from fastapi import APIRouter

userConfig = None
try:
    from nexyconfig import NexyConfig as UserNexyConfig
    userConfig = UserNexyConfig()
except ImportError:
    pass




class NexyConfig:
    ALIASES: dict[str, str] = userConfig.ALIASES if userConfig else {"@": "src/components"}
    NAMESPACE: str = "__nexy__/"
    # MARKDOWN_EXTENSIONS: list[str] = ['extra', 'codehilite'] + userConfig.MARKDOWN_EXTENSIONS if userConfig and userConfig.MARKDOWN_EXTENSIONS else ['extra', 'codehilite']
    MARKDOWN_EXTENSIONS: list[str] = ['extra', 'codehilite']
    TARGET_EXTENSIONS: list[str] = ['.nexy', '.mdx']
    ROUTE_FILE_EXTENSIONS: list[str] = ['.nexy', '.mdx',".py"]
    ROUTE_FILE_EXCEPTIONS: list[str] =["__init__.py", "layout.nexy"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy","index.mdx"]
    PROJECT_ROOT: str = "."
    ROUTER_PATH: str = "src/routes"
    FILE_BASED_ROUTING: bool = userConfig.FILE_BASED_ROUTING if userConfig else True
    ROOT_MODULE: APIRouter | None = userConfig.ROOT_MODULE if userConfig else None




