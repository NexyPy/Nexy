from contextvars import ContextVar

from fastapi import Request

current_request: ContextVar[Request | None] = ContextVar("current_request", default=None)
