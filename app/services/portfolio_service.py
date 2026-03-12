from __future__ import annotations

from typing import List

from app.db import db
from app.errors import BadRequestError, NotFoundError
from app.models import Portfolio, User


def create_portfolio(name: str, description: str, user: User) -> int:
    if not name or not user:
        raise BadRequestError('Portfolio name and owner are required')
    portfolio = Portfolio(name=name, description=description, user=user)
    db.session.add(portfolio)
    db.session.flush()
    return portfolio.id


def get_portfolios_by_user(user: User) -> List[Portfolio]:
    return db.session.query(Portfolio).filter_by(owner=user.username).all()


def get_all_portfolios() -> List[Portfolio]:
    return db.session.query(Portfolio).all()


def get_portfolio_by_id(portfolio_id: int) -> Portfolio | None:
    return db.session.query(Portfolio).filter_by(id=portfolio_id).one_or_none()


def require_portfolio(portfolio_id: int) -> Portfolio:
    portfolio = get_portfolio_by_id(portfolio_id)
    if not portfolio:
        raise NotFoundError(f'Portfolio {portfolio_id} not found')
    return portfolio


def delete_portfolio(portfolio_id: int) -> None:
    portfolio = require_portfolio(portfolio_id)
    db.session.delete(portfolio)
    db.session.flush()
