import hashlib
from typing import Callable, Dict

class ActionsStore:
    def __init__(self):
        self.registry: Dict[str, Callable] = {}
        self.path_map: Dict[str, str] = {}

    def _generate_hash(self, func_id: str) -> str:
        return hashlib.sha256(f"{func_id}salt2026".encode()).hexdigest()[:12]

    def register(self, func: Callable):
        func_id = f"{func.__module__}.{func.__name__}"
        self.registry[func_id] = func
        return func_id


ACTIONS_STORE = ActionsStore()