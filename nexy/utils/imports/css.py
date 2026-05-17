from typing import Callable

class CSS:
    @staticmethod
    def create(path: str) -> Callable[[], str]:
        # CSS imports in Nexy logic usually return empty strings 
        # as they are injected in the head during compilation
        return lambda: ""