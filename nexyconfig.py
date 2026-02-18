from dataclasses import dataclass
from typing import Optional, Union
from src.app.app_module import AppModule
from nexy.router import FileBasedRouter



class NexyConfig():
    ALIASES: dict[str, str] = {"@": "src/components"}
    useRouter = FileBasedRouter
