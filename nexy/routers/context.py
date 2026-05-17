from contextvars import ContextVar
from typing import Optional
from fastapi import Request


current_request: ContextVar[Optional[Request]] = ContextVar("current_request", default=None)