from __future__ import annotations

from app.db import db
from app.errors import BadRequestError, ConflictError, NotFoundError
from app.models import PortfolioAccess

ROLE_VIEWER = 'viewer'
ROLE_MANAGER = 'manager'
VALID_ROLES = {ROLE_VIEWER, ROLE_MANAGER}


def grant_access(portfolio_id: int, user_id: str, role: str) -> PortfolioAccess:
    role = role.lower().strip()
    if role not in VALID_ROLES:
        raise BadRequestError(f'Invalid role: {role}')

    from app.services.portfolio_service import get_portfolio_by_id
    from app.services.user_service import get_user_by_username

    portfolio = get_portfolio_by_id(portfolio_id)
    if portfolio is None:
        raise NotFoundError(f'Portfolio {portfolio_id} not found')
    if get_user_by_username(user_id) is None:
        raise NotFoundError(f'User {user_id} not found')
    if portfolio.owner == user_id:
        raise ConflictError('Portfolio owner already has full access')

    existing = db.session.query(PortfolioAccess).filter_by(portfolio_id=portfolio_id, user_id=user_id).one_or_none()
    if existing:
        existing.role = role
        db.session.flush()
        return existing

    grant = PortfolioAccess(portfolio_id=portfolio_id, user_id=user_id, role=role)
    db.session.add(grant)
    db.session.flush()
    return grant


def revoke_access(portfolio_id: int, user_id: str) -> bool:
    grant = db.session.query(PortfolioAccess).filter_by(portfolio_id=portfolio_id, user_id=user_id).one_or_none()
    if not grant:
        return False
    db.session.delete(grant)
    db.session.flush()
    return True


def has_access(portfolio_id: int, principals: set[str], required_role: str | None = None) -> bool:
    if not principals:
        return False

    grants = db.session.query(PortfolioAccess).filter(PortfolioAccess.portfolio_id == portfolio_id).all()
    for grant in grants:
        if grant.user_id in principals:
            if required_role is None:
                return True
            if required_role == ROLE_VIEWER and grant.role in {ROLE_VIEWER, ROLE_MANAGER}:
                return True
            if required_role == ROLE_MANAGER and grant.role == ROLE_MANAGER:
                return True
    return False
