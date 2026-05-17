from __future__ import annotations

from dataclasses import dataclass

from fastapi import Response


@dataclass(frozen=True)
class NexyCompileError(Exception):
    source_path: str
    message: str
    line: int | None = None
    column: int | None = None

    def __str__(self) -> str:
        loc = ""
        if self.line is not None:
            col = self.column if self.column is not None else 0
            loc = f":{self.line}:{col}"
        return f"{self.source_path}{loc} - {self.message}"


def NotFound() -> Response:
    return Response(
        content="<style>*{padding: 0; margin: 0;box-sizing: border-box;}</style><body  style='background-color: yellow;overflow: hidden; height: 100vh;  display: flex; justify-content: center; align-items: center;font-family:  sans-serif;'><h2 style='font-size: 6rem;  border-right: 1px solid red; padding-right: 10px; margin-left: 4rem;'>404</h2> <div style='padding: 1rem; background-color: transparent;'><h2 style='color: red;'>Not Found</h2><p style='width:14rem;margin-top: .5rem;'>Nexy do not find the requested resource.</p></div></body>",
        status_code=404,
    )


def InternalServerError() -> Response:
    return Response(
        content="<style>*{padding: 0; margin: 0;box-sizing: border-box;}</style><body  style='background-color: red;overflow: hidden; height: 100vh; gap: 1rem; display: flex; justify-content: center; align-items: center; text-align: center ;font-family:  sans-serif;'><h2 style='font-size: 3rem; color: red; border-right: 1px solid red; padding-right: 10px;'>500</h2> Internal Server Error</body>",
        status_code=500,
    )
