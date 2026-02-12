class NexyConfig:
    ALIASES: dict[str, str] = {"@": "src/components"}
    NAMESPACE: str = "__nexy__/"
    MARKDOWN_EXTENSIONS: list[str] = ['extra', 'codehilite']
    TARGET_EXTENSIONS: list[str] = ['.nexy', '.mdx']
    ROUTE_FILE_EXTENSIONS: list[str] = ['.nexy', '.mdx',".py"]
    ROUTE_FILE_EXCEPTIONS: list[str] = ["__init__.py", "layout.nexy"]
    ROUTE_FILE_DEFAULT: list[str] = ["index.py", "index.nexy","index.mdx"]
    PROJECT_ROOT: str = "."
    ROUTER_PATH: str = "src/routes"
    FILE_BASED_ROUTING: bool = True


