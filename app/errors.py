from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ApiError(Exception):
    error: str
    detail: Any = None
    status_code: int = 400


class AuthenticationError(ApiError):
    def __init__(self, detail: Any = 'Authentication failed'):
        super().__init__('forbidden', detail, 403)


class AuthorizationError(ApiError):
    def __init__(self, detail: Any = 'Not authorized for this resource'):
        super().__init__('forbidden', detail, 403)


class NotFoundError(ApiError):
    def __init__(self, detail: Any = 'Resource not found'):
        super().__init__('not_found', detail, 404)


class ConflictError(ApiError):
    def __init__(self, detail: Any = 'Conflict'):
        super().__init__('conflict', detail, 409)


class BadRequestError(ApiError):
    def __init__(self, detail: Any = 'Bad request'):
        super().__init__('bad_request', detail, 400)
