import inspect
import re
from collections.abc import Callable
from typing import Any


class RouteValidator:
    @staticmethod
    def extract_path_params(path: str) -> set[str]:
        return {m.group(1) for m in re.finditer(r"{([^}:]+)(:[^}]+)?}", path)}

    @classmethod
    def validate_sig(cls, handler: Callable[..., Any], path: str, method_name: str):
        expected = cls.extract_path_params(path)
        if not expected:
            return

        try:
            sig = inspect.signature(handler)
            params = set(sig.parameters.keys())
            missing = expected - params
            if missing:
                raise RuntimeError(
                    f"Signature mismatch for '{method_name}' at path '{path}': "
                    f"missing parameters: {', '.join(sorted(missing))}"
                )
        except ValueError:
            pass
