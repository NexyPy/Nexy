import base64
import mimetypes
from pathlib import Path
from typing import Callable
from nexy.core.config import Config

class Image:
    @staticmethod
    def create(path: str) -> Callable[[], str]:
        try:
            p = Path(path)
            if not p.is_absolute():
                p = Path(Config.PROJECT_ROOT).joinpath(path)
            
            data = p.read_bytes()
            mime, _ = mimetypes.guess_type(str(p))
            mime = mime or "application/octet-stream"
            
            b64 = base64.b64encode(data).decode("ascii")
            return lambda: f"data:{mime};base64,{b64}"
        except Exception:
            return lambda: ""