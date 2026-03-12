from __future__ import annotations

from flask import g

from app.errors import AuthorizationError
from app.models import Portfolio
from app.services import portfolio_access_service


def _principals() -> set[str]:
    principals: set[str] = set()
    for key in ('current_username', 'current_user_id'):
        value = getattr(g, key, None)
        if value:
            principals.add(str(value))
    return principals


def require_owner(portfolio: Portfolio) -> None:
    if getattr(g, 'current_username', None) != portfolio.owner:
        raise AuthorizationError('Only portfolio owner can perform this action')


def require_view_permission(portfolio: Portfolio) -> None:
    if getattr(g, 'current_username', None) == portfolio.owner:
        return
    if portfolio_access_service.has_access(portfolio.id, _principals(), required_role=portfolio_access_service.ROLE_VIEWER):
        return
    raise AuthorizationError('Viewer access required')


def require_manager_permission(portfolio: Portfolio) -> None:
    if getattr(g, 'current_username', None) == portfolio.owner:
        return
    if portfolio_access_service.has_access(portfolio.id, _principals(), required_role=portfolio_access_service.ROLE_MANAGER):
        return
    raise AuthorizationError('Manager access required')
