import importlib
import json
import traceback
from typing import Any

from fastapi import Request
from fastapi.responses import HTMLResponse

from nexy import Vite
from nexy.core.config import Config
from nexy.core.string import StringTransform

str_tools = StringTransform()


def _get_req() -> Request:
    from .routers.context import current_request

    req = current_request.get()
    if not req:
        raise RuntimeError(
            "Navigation hooks can only be called within the context of an HTTP request."
        )
    return req


def usePathname() -> str:
    return _get_req().url.path


def useSearchParams() -> dict:
    return dict(_get_req().query_params)


def useRouter() -> dict:
    req = _get_req()
    return {
        "path": req.url.path,
        "base_url": str(req.base_url),
        "url_for": req.app.url_for if req.app else None,
    }


def useQuery() -> dict:
    return _get_req().path_params


def useSession() -> dict:
    return getattr(_get_req(), "session", {})


def useCookies() -> dict:
    return _get_req().cookies


PYTHON_VIEWS = (".nexy", ".mdx")
FRONTEND_VIEWS = (".tsx", ".vue", ".svelte", ".jsx")


def useViews(path: str, context: dict[str, Any] | None = None) -> HTMLResponse:
    ctx = context or {}

    if path.endswith(PYTHON_VIEWS):
        mapped = str_tools.normalize_route_path_for_namespace(path)
        import_path = f"{Config.NAMESPACE}{mapped}".replace("/", ".").rsplit(".", 1)[0]

        try:
            module = importlib.import_module(import_path)

            file_name = path.split("/")[-1].split(".", 1)[0]
            func_name = str_tools.get_component_name(file_name)
            component_func = getattr(module, func_name)
            return HTMLResponse(Vite() + component_func(**ctx))

        except (ImportError, AttributeError) as e:
            traceback.print_exc()
            raise ValueError(f"Failed to load module or function for path: {path}") from e

    elif any(ext in path for ext in FRONTEND_VIEWS):
        # KISS: Map extension to framework and return an hydratable container
        ext = f".{path.split('.')[-1]}"
        framework = Config.FRONTEND_EXTENSIONS.get(ext, "react")

        # Prepare props for hydration
        props_json = json.dumps(ctx)

        # Hydratable container that Nexy's frontend runtime will pick up
        container = (
            f'<div data-nexy-fw="{framework}" '
            f'data-nexy-path="{path}" '
            f"data-nexy-props='{props_json}'>"
            f"</div>"
        )

        return HTMLResponse(Vite() + container)

    else:
        raise ValueError(f"Unsupported view type for path: {path}")
