import json
from pathlib import Path
from typing import Any, Callable
from nexy.core.config import Config

class Json:
    @staticmethod
    def create(path: str) -> Callable[[], Any]:
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(Config.PROJECT_ROOT).joinpath(path)
                
            with p.open("r", encoding="utf-8") as f:
                result = json.load(f)
                return lambda: result
        except Exception:
            return lambda: {}